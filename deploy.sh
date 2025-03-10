# Install required packages.
sudo apt-get update
mkdir ~/.cloudshell touch ~/.cloudshell/no-apt-get-warning
sudo apt-get install fzf

# Select target project for installation.
projects=($(gcloud projects list --format="value(projectId)"))
selected_project=$(printf "%s\n" "${projects[@]}" | fzf --prompt="Select a project: ")

if [[ -n $selected_project ]]; then
    echo "Selected project: $selected_project"
    export GOOGLE_CLOUD_PROJECT="$selected_project"
else
    echo "No project selected."
fi

echo "Setting Project ID: ${GOOGLE_CLOUD_PROJECT}"
gcloud config set project ${GOOGLE_CLOUD_PROJECT}

# Enable the APIs.
REQUIRED_APIS=(
  storage.googleapis.com
  compute.googleapis.com
  run.googleapis.com
  cloudbuild.googleapis.com
  cloudresourcemanager.googleapis.com
  artifactregistry.googleapis.com
)

for API in "${REQUIRED_APIS[@]}"; do
  gcloud services enable "$API"
done

# Check for existing OAuth Consent Screen.
iap_brand_id=$(gcloud iap oauth-brands list --format="value(name)" | sed "s:.*/::")

if [[ -z "$iap_brand_id" ]]; then
  echo "Error: No IAP OAuth brand found. Please configure the OAuth consent screen and ensure it is set to INTERNAL."
  exit 1
fi

# Select target region for installation.
regions=($(gcloud compute regions list --format="value(name)"))
PS3="Select a region: "
select selected_region in "${regions[@]}"; do
    if [[ -n $selected_region ]]; then
        echo "Selected region: $selected_region"
        export GOOGLE_CLOUD_REGION="$selected_region"
        break
    else
        echo "Invalid choice, please select a valid region."
    fi
done

echo "Setting Region: ${GOOGLE_CLOUD_REGION}"
gcloud config set compute/region ${GOOGLE_CLOUD_REGION}

# Get consent for tracking usage.
opt_out="N"
read -p "Do you want to opt out of sending usage information to Google? (N/n) " yn

if [[ -z "$yn" ]]; then
  yn="$opt_out"
fi

yn=$(tr '[:upper:]' '[:lower:]' <<< "$yn")

if [[ "$yn" == "y" || "$yn" == "yes" ]]; then
  echo "You have opted out."
  OPT_OUT=true
else
  echo "You have not opted out."
  OPT_OUT=false
fi

# Setup Terraform backend bucket.
default_state_bucket_name="${GOOGLE_CLOUD_PROJECT}-tfstate"

echo "Hello, $terraform_state_bucket_name!"

echo "Do you already have a Terraform state bucket? (yes/no)"
read -r has_bucket

if [[ "$has_bucket" == "y" || "$has_bucket" == "yes" ]]; then
  echo "Enter the existing bucket name:"
  read -r terraform_state_bucket_name
else
  echo "Would you like to create a new Terraform state bucket? (yes/no)"
  read -r create_bucket

  if [[ "$create_bucket" == "y" || "$create_bucket" == "yes" ]]; then
    read -r -p "Enter a name for the new bucket (${default_state_bucket_name}):" terraform_state_bucket_name
    terraform_state_bucket_name=${terraform_state_bucket_name:-${default_state_bucket_name}}
    
    echo "Creating Terraform state cloud storage bucket..."
    gcloud storage buckets create gs://${terraform_state_bucket_name} \
      --project=${GOOGLE_CLOUD_PROJECT}

    echo "Enabling versioning on the bucket..."
    gcloud storage buckets update gs://${terraform_state_bucket_name} \
      --versioning
  else
    echo "No bucket provided. Exiting."
    exit 1
  fi
fi
echo "Terraform state bucket set to: $terraform_state_bucket_name"

# Create Artifact Registry repository if it doesn't exist.
if gcloud artifacts repositories describe genmedia-studio --location="${GOOGLE_CLOUD_REGION}" --format="value(name)" 2>/dev/null; then
  echo "Repository genmedia-studio already exists in ${GOOGLE_CLOUD_REGION}. Skipping creation."
else
  echo "Repository genmedia-studio does not exist in ${GOOGLE_CLOUD_REGION}. Creating..."
  gcloud artifacts repositories create genmedia-studio \
    --location="${GOOGLE_CLOUD_REGION}" \
    --repository-format=docker \
    --description="Docker repository for GenMedia Studio." || exit 1
fi

# Build, push and deploy images.
gcloud builds submit --config cloudbuild.yaml --substitutions=_TF_STATE_BUCKET=$terraform_state_bucket_name .