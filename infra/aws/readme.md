
# setup
1. install CLI
```
install-cli.sh
```
2. configure `aws` cli: provide your credentials from the `user.csv`
```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: eu-central-1
Default output format [None]: json
```
4. check it is setup
```
cat ~/.aws/credentials
```
5. setup and download the EC2 SSH key `amazon.pem`; you will use it to connect to EC2 instances, when needed.
