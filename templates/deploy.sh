aws cloudformation create-stack \
 --stack-name network-stack \
 --template-body file://1-network.yaml \
 --capabilities CAPABILITY_NAMED_IAM

aws cloudformation update-stack \
 --stack-name network-stack \
 --template-body file://1-network.yaml \
 --capabilities CAPABILITY_NAMED_IAM

aws cloudformation create-stack \
 --stack-name rds-instance-stack \
 --template-body file://2-rds-instance.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"DBUsername","ParameterValue":"admin"},{"ParameterKey":"DBPassword","ParameterValue":"Admin2024"}]'

aws cloudformation create-stack \
 --stack-name rds-cluster-stack \
 --template-body file://3-rds-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"DBUsername","ParameterValue":"admin"},{"ParameterKey":"DBPassword","ParameterValue":"Admin2024"}]'

aws cloudformation create-stack \
 --stack-name rds-cluster-stack \
 --template-body file://4-aurora-cluster.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters '[{"ParameterKey":"MasterUsername","ParameterValue":"admin"},{"ParameterKey":"MasterUserPassword","ParameterValue":"Admin2024"}]'