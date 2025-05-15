

 aws ecr get-login-password | docker login --username AWS --password-stdin 524196012679.dkr.ecr.eu-central-1.amazonaws.com

REPO_NAME=sg/java-app-demos
ACCOUNT_ID=524196012679
REGION=eu-central-1
ECR_URL=524196012679.dkr.ecr.eu-central-1.amazonaws.com
TAGS=$(aws ecr describe-images --repository-name $REPO_NAME --query 'imageDetails[].imageTags[]' --output text | grep -o 'v[0-9]\+' | sort -V | tail -n1)
NEXT_TAG="v$(( ${TAGS/v/} + 1 ))"

docker pull nginx
docker tag nginx:latest $ECR_URL/$REPO_NAME:$NEXT_TAG
docker push $ECR_URL/$REPO_NAME:$NEXT_TAG

echo "✅ Docker image nginx pushed with tag: $NEXT_TAG"
