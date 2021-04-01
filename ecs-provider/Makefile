NAME ?= dog-names
TAG ?= 001
IMAGE_NAME = $(NAME):$(TAG)

deploy :
	IMAGE_TAG=$(TAG) cdk deploy --all
.PHONY: deploy

synth :
	IMAGE_TAG=$(TAG) cdk synth
.PHONY: synth

destroy :
	IMAGE_TAG=$(TAG) cdk destroy --all
.PHONY: destroy

## Helpers to build and push to ECR

image :
	docker build -t $(IMAGE_NAME) ./image
.PHONY: image

login :
	aws ecr get-login-password | docker login \
		--username AWS \
		--password-stdin $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
.PHONY: login

tag :
	docker tag $(IMAGE_NAME) $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME)
.PHONY: tag

push : tag
	docker push $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME)
.PHONY: push

