// Create (or reuse) the Autoinks EC2 server (its own box, separate from TurtleReels): key pair, firewall, Ubuntu 24.04 t3.small, Elastic IP.
// Uses the AWS credentials in ~/.aws. Safe to re-run: existing pieces are found by name and reused.
//
//   node deploy/aws-provision.mjs
//
// Needs @aws-sdk/client-ec2 (resolved from AWS_SDK_FROM, default D:/Marketplace).
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(path.join(process.env.AWS_SDK_FROM || 'D:/Marketplace', 'package.json'));
const {
  EC2Client, DescribeKeyPairsCommand, CreateKeyPairCommand, DescribeVpcsCommand, DescribeSecurityGroupsCommand,
  CreateSecurityGroupCommand, AuthorizeSecurityGroupIngressCommand, DescribeImagesCommand, DescribeInstancesCommand,
  RunInstancesCommand, DescribeAddressesCommand, AllocateAddressCommand, AssociateAddressCommand, waitUntilInstanceRunning,
} = require('@aws-sdk/client-ec2');

const REGION = process.env.AWS_REGION_TR || 'ap-south-1';
const NAME = 'autoinks';
const KEY_NAME = 'autoinks-key';
const KEY_FILE = path.join(os.homedir(), '.ssh', 'autoinks.pem');
const SG_NAME = 'autoinks-sg';
const TYPE = 't3.small';
const ec2 = new EC2Client({ region: REGION });
const tag = (Name) => [{ Key: 'Name', Value: Name }, { Key: 'app', Value: NAME }];

const myIp = (await (await fetch('https://checkip.amazonaws.com')).text()).trim();
console.log(`Region ${REGION}. This PC's IP: ${myIp}`);

// 1. key pair (private key saved once, readable only by you)
const keys = await ec2.send(new DescribeKeyPairsCommand({ Filters: [{ Name: 'key-name', Values: [KEY_NAME] }] }));
if (!keys.KeyPairs.length) {
  const k = await ec2.send(new CreateKeyPairCommand({ KeyName: KEY_NAME, KeyType: 'ed25519', TagSpecifications: [{ ResourceType: 'key-pair', Tags: tag(KEY_NAME) }] }));
  fs.mkdirSync(path.dirname(KEY_FILE), { recursive: true });
  fs.writeFileSync(KEY_FILE, k.KeyMaterial.endsWith('\n') ? k.KeyMaterial : `${k.KeyMaterial}\n`);
  if (process.platform === 'win32') {
    execFileSync('icacls', [KEY_FILE, '/inheritance:r', '/grant:r', `${os.userInfo().username}:R`], { stdio: 'ignore' });
  } else fs.chmodSync(KEY_FILE, 0o400);
  console.log(`Key pair created, private key saved to ${KEY_FILE}`);
} else if (!fs.existsSync(KEY_FILE)) {
  throw new Error(`Key pair ${KEY_NAME} exists in AWS but ${KEY_FILE} is missing. Delete the key pair in the console and re-run.`);
} else console.log(`Key pair ${KEY_NAME} already exists`);

// 2. security group in the default VPC: SSH from this PC only, web from anywhere
const { Vpcs } = await ec2.send(new DescribeVpcsCommand({ Filters: [{ Name: 'is-default', Values: ['true'] }] }));
if (!Vpcs.length) throw new Error(`No default VPC in ${REGION}`);
const vpcId = Vpcs[0].VpcId;
let sg = (await ec2.send(new DescribeSecurityGroupsCommand({ Filters: [{ Name: 'group-name', Values: [SG_NAME] }, { Name: 'vpc-id', Values: [vpcId] }] }))).SecurityGroups[0];
if (!sg) {
  const { GroupId } = await ec2.send(new CreateSecurityGroupCommand({
    GroupName: SG_NAME, Description: 'Autoinks web server', VpcId: vpcId,
    TagSpecifications: [{ ResourceType: 'security-group', Tags: tag(SG_NAME) }],
  }));
  sg = { GroupId, IpPermissions: [] };
  console.log(`Security group ${SG_NAME} created`);
}
const has = (port, cidr) => sg.IpPermissions.some((p) => p.FromPort === port && (p.IpRanges || []).some((r) => r.CidrIp === cidr));
const rules = [[22, `${myIp}/32`, 'SSH from admin PC'], [80, '0.0.0.0/0', 'HTTP (redirects to HTTPS)'], [443, '0.0.0.0/0', 'HTTPS']]
  .filter(([port, cidr]) => !has(port, cidr));
if (rules.length) {
  await ec2.send(new AuthorizeSecurityGroupIngressCommand({
    GroupId: sg.GroupId,
    IpPermissions: rules.map(([port, cidr, Description]) => ({ IpProtocol: 'tcp', FromPort: port, ToPort: port, IpRanges: [{ CidrIp: cidr, Description }] })),
  }));
  console.log(`Firewall rules added: ${rules.map((r) => `${r[0]} from ${r[1]}`).join(', ')}`);
}

// 3. instance (reuse a running/stopped one tagged app=autoinks)
let inst = (await ec2.send(new DescribeInstancesCommand({ Filters: [
  { Name: 'tag:app', Values: [NAME] }, { Name: 'instance-state-name', Values: ['pending', 'running', 'stopping', 'stopped'] },
] }))).Reservations.flatMap((r) => r.Instances)[0];
if (!inst) {
  const { Images } = await ec2.send(new DescribeImagesCommand({
    Owners: ['099720109477'], // Canonical
    Filters: [{ Name: 'name', Values: ['ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*'] }, { Name: 'state', Values: ['available'] }],
  }));
  const ami = Images.sort((a, b) => b.CreationDate.localeCompare(a.CreationDate))[0];
  if (!ami) throw new Error('Ubuntu 24.04 image not found');
  console.log(`Launching ${TYPE} with ${ami.Name}`);
  const run = await ec2.send(new RunInstancesCommand({
    ImageId: ami.ImageId, InstanceType: TYPE, KeyName: KEY_NAME, SecurityGroupIds: [sg.GroupId], MinCount: 1, MaxCount: 1,
    BlockDeviceMappings: [{ DeviceName: ami.RootDeviceName, Ebs: { VolumeSize: 30, VolumeType: 'gp3', DeleteOnTermination: true, Encrypted: true } }],
    MetadataOptions: { HttpTokens: 'required' },
    TagSpecifications: [{ ResourceType: 'instance', Tags: tag(NAME) }, { ResourceType: 'volume', Tags: tag(`${NAME}-disk`) }],
  }));
  inst = run.Instances[0];
}
console.log(`Instance ${inst.InstanceId} (${inst.State?.Name}). Waiting until running…`);
await waitUntilInstanceRunning({ client: ec2, maxWaitTime: 300 }, { InstanceIds: [inst.InstanceId] });

// 4. Elastic IP so the address (and DuckDNS record) never changes
let addr = (await ec2.send(new DescribeAddressesCommand({ Filters: [{ Name: 'tag:app', Values: [NAME] }] }))).Addresses[0];
if (!addr) {
  const a = await ec2.send(new AllocateAddressCommand({ Domain: 'vpc', TagSpecifications: [{ ResourceType: 'elastic-ip', Tags: tag(`${NAME}-ip`) }] }));
  addr = { AllocationId: a.AllocationId, PublicIp: a.PublicIp };
  console.log(`Elastic IP allocated: ${a.PublicIp}`);
}
if (addr.InstanceId !== inst.InstanceId) {
  await ec2.send(new AssociateAddressCommand({ AllocationId: addr.AllocationId, InstanceId: inst.InstanceId }));
}

console.log('\nREADY');
console.log(`  instance : ${inst.InstanceId} (${TYPE}, ${REGION})`);
console.log(`  address  : ${addr.PublicIp}`);
console.log(`  ssh      : ssh -i "${KEY_FILE}" ubuntu@${addr.PublicIp}`);
