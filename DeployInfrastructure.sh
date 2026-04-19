cd infrastructure
terraform plan -var="environment=$env" -var="Response_image_uri=$response_image_uri" -var="SpeechToText_image_uri=$speechtotext_image_uri"