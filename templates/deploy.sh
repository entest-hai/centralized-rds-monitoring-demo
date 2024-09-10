# create network stack
aws cloudformation create-stack \
 --stack-name network-stack \
 --template-body file://1-network.yaml \
 --capabilities CAPABILITY_NAMED_IAM

# update network stack
aws cloudformation update-stack \
 --stack-name network-stack \
 --template-body file://1-network.yaml \
 --capabilities CAPABILITY_NAMED_IAM

# create rds mysql instance
aws cloudformation update-stack \
 --stack-name rds-instance-stack \
 --template-body file://2-rds-instance.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"NetworkStackName","ParameterValue":"network-database"},{"ParameterKey":"DBUsername","ParameterValue":"admin"},{"ParameterKey":"DBPassword","ParameterValue":"Password"}]'

# create rds mysql cluster 
aws cloudformation create-stack \
 --stack-name rds-cluster-stack \
 --template-body file://3-rds-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"NetworkStackName","ParameterValue":"network-database"},{"ParameterKey":"DBUsername","ParameterValue":"admin"},{"ParameterKey":"DBPassword","ParameterValue":"Password"}]'

# update rds mysql cluster
aws cloudformation update-stack \
 --stack-name rds-cluster-stack \
 --template-body file://3-rds-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"NetworkStackName","ParameterValue":"network-database"},{"ParameterKey":"DBUsername","ParameterValue":"admin"},{"ParameterKey":"DBPassword","ParameterValue":"Password"}]'

# create aurora mysql cluster 
aws cloudformation create-stack \
 --stack-name aurora-cluster-stack \
 --template-body file://4-aurora-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"NetworkStackName","ParameterValue":"network-database"},{"ParameterKey":"MasterUsername","ParameterValue":"admin"},{"ParameterKey":"MasterUserPassword","ParameterValue":"Password"}]'

# create aurora mysql cluster 
aws cloudformation update-stack \
 --stack-name aurora-cluster-stack \
 --template-body file://4-aurora-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"NetworkStackName","ParameterValue":"network-database"},{"ParameterKey":"MasterUsername","ParameterValue":"admin"},{"ParameterKey":"MasterUserPassword","ParameterValue":"Password"}]'

# create ecs cluster
aws cloudformation create-stack \
--stack-name ecs-cluster-stack \
--template-body file://7-ecs-cluster.yaml \
--capabilities CAPABILITY_NAMED_IAM

# create ecs task definition
aws cloudformation create-stack \
 --stack-name mysql-app-task-definition \
 --template-body file://8-task-def-mysql-app.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"AppECRImageURL","ParameterValue":"111222333444.dkr.ecr.ap-southeast-1.amazonaws.com/mysql-app:latest"}]'

# create ecs task definition 
aws cloudformation update-stack \
 --stack-name mysql-app-task-definition \
 --template-body file://8-task-def-mysql-app.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"AppECRImageURL","ParameterValue":"111222333444.dkr.ecr.ap-southeast-1.amazonaws.com/mysql-app:latest"}]'

# run ecs tasks enable exec
aws ecs run-task \
 --cluster arn:aws:ecs:ap-southeast-1:111222333444:cluster/demo \
 --task-definition arn:aws:ecs:ap-southeast-1:111222333444:task-definition/mysql-app:2 \
 --enable-execute-command \
 --launch-type FARGATE \
 --count 10 \
 --network-configuration "awsvpcConfiguration={subnets=[subnet-id],securityGroups=[sg-id],assignPublicIp=ENABLED}"

# eventbridge schedule ecs task 
aws cloudformation create-stack \
 --stack-name schedule-mysql-app \
 --template-body file://9-schedule-mysql-app.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"ClusterName","ParameterValue":"demo"},{"ParameterKey":"SecurityGroups","ParameterValue":"sg-id"},{"ParameterKey":"Subnets","ParameterValue":"subnet-id"},{"ParameterKey":"TaskName","ParameterValue":"mysql-app"}]'