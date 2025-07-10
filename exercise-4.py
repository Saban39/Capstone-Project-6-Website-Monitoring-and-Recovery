import boto3
import logging
from operator import itemgetter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

ecr_client = boto3.client('ecr')

# Get all ECR repositories
try:
    repos = ecr_client.describe_repositories()['repositories']
    logging.info("Fetched ECR repositories successfully.")
    print("Available ECR repositories:")
    for repo in repos:
        print(repo['repositoryName'])
        logging.info(f"Repository found: {repo['repositoryName']}")
except Exception as e:
    logging.error(f"Error fetching ECR repositories: {e}")
    raise

print("-----------------------")

# For one specific repo, get all the images and print them sorted by date
repo_name = "sg/java-app-demos"

try:
    images = ecr_client.describe_images(repositoryName=repo_name)
    logging.info(f"Fetched images from repository: {repo_name}")
except Exception as e:
    logging.error(f"Error fetching images from repository '{repo_name}': {e}")
    raise

image_tags = []

for image in images['imageDetails']:
    tags = image.get('imageTags', ['<untagged>'])  # Handle images with no tag
    pushed_at = image['imagePushedAt']
    image_tags.append({
        'tag': tags,
        'pushed_at': pushed_at
    })
    logging.debug(f"Image found - Tags: {tags}, Pushed At: {pushed_at}")

# Sort images by pushed date descending
images_sorted = sorted(image_tags, key=itemgetter("pushed_at"), reverse=True)

print(f"Images for repository '{repo_name}' sorted by date:")
for image in images_sorted:
    print(image)
    logging.info(f"Image: {image}")
