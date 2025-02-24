<!--markdownlint-disable MD024 MD033 MD036 MD041 -->
<walkthrough-metadata>
  <meta name="title" content="Google Cloud Platform" />
  <meta name="description" content="Learn how to build and run containerized
  services, use automated build and deployment tools, implement Google Cloud
  APIs to leverage GenAI capabilities and operate your service in production
  ." />
  <meta name="keywords" content="cloud, python, containers, console, run, AI,
  GenAI, APIs" />
</walkthrough-metadata>

# AI Agents made easy

Welcome to this hands-on tutorial in which you will learn how to build a very
clever AI Agent with help of our latest Gemini and Imagen models.

<walkthrough-info-message>Google is phasing out 3rd party cookies in Chrome to
better protect the privacy of its users. If you are attempting this tutorial on
Chrome, please make sure that 3rd party cookies are enabled in Chrome's address
bar (the icon that looks like an eye), since the tutorial still requires these.
The same is required for any other browser.</walkthrough-info-message>

## Overview

![Tutorial header image](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/containers.jpg)

In this interactive tutorial, you will learn how to build and run containerized
AI agent written in Python and use automated build and deployment tools to release
to production in matter of minutes.

The tutorial is split into **3 modules**:

**Module 1** will explore Gemini's Function Calling feature. We will be adding new
 methods to fetch data from Firestore and manipulate your character 3D models a little bit.

**Module 2** will show  you how to work with RAG (Retrieval Augmented Generation). 
in Vertex AI with help of our Python SDK.

**Module 3** will get you familiar with Cloud Build, a fully-managed
container-based build system. 

Hope you're not afraid to get your hands dirty. Make sure get a beverage and
some snacks of your choice, strap in and hit 'Start'.

## Module 1: Let's get the project running

![Tutorial header image](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/run.jpg)

In this module we will deploy this project with help of Terraform and Cloud Build. This will
give us a working URL where we can test our changes. 

[Overview on Cloud Run](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/overview-run.png)

<walkthrough-tutorial-difficulty difficulty="2"></walkthrough-tutorial-difficulty>

Estimated time:
<walkthrough-tutorial-duration duration="30"></walkthrough-tutorial-duration>

To get started, click **Start**.

## Project setup

First, let's make sure we got the correct project selected. Go ahead and select
the provided project ID.

<walkthrough-project-setup billing="true"></walkthrough-project-setup>

<walkthrough-enable-apis apis="cloudbuild.googleapis.com,
run.googleapis.com,
aiplatform.googleapis.com,
firestore.googleapis.com,
artifactregistry.googleapis.com,
cloudresourcemanager.googleapis.com"></walkthrough-enable-apis>

You can use the builtin
<walkthrough-editor-spotlight spotlightId="menu-terminal-new-terminal"> Cloud
Shell Terminal </walkthrough-editor-spotlight> to run the gcloud command.

## Project preparation

Before we beging, there are some things we need to prepare, such as hydrate Firestore and upload 
some dummy documents for RAG.

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region us-central1
gcloud config set artifacts/location us-central1
gcloud firestore databases create --location us-central1

gcloud storage buckets create gs://build-you-ai-agent-<walkthrough-project-number/> --location=us-central1
gsutil cp -r data/* gs://build-you-ai-agent-<walkthrough-project-number/>

gcloud firestore import gs://build-you-ai-agent-<walkthrough-project-number/>/firestore-data --database="(default)"
```


## Exploring the code

Take some time and
<walkthrough-editor-open-file filePath="cloudshell_open/build-your-ai-agent/app.py">
familiarize yourself with the code. </walkthrough-editor-open-file>

Once you've understood what's going on, you can try to run that app directly in
Cloud Shell, running the following in the terminal:

```bash
pip install -r requirements.txt
export PROJECT_ID=<walkthrough-project-id/>
export REGION=us-central1

python -m flask run --host=0.0.0.0 --port=8080 --debugger --reload
```

This downloads dependencies, imports initial data to firestore and starts the web server. 
You can now use Cloud Shell Web Preview on port 8080 to check out your application. 
You can find the Web Preview <walkthrough-web-preview-icon></walkthrough-web-preview-icon> at
the top right in Cloud Shell. If you don't see a response from the web server,
try waiting a little longer for the Go compiler to build and start your server.

Finally, focus the terminal again and terminate the web server with `Ctrl-C`.

## Building and deploying the code

We established that our code runs locally, great! Let's put it on the cloud.

In the following steps, we'll deploy our app to Cloud Run, which is a compute
platform for running modern, cloud-first, containerized applications. Cloud Run
schedules and runs container images that expose services over HTTP. You can use
any programming language or framework, as long as you can bind an HTTP server on
a port provided by the `$PORT` environment variable. Please note that container
images must be in Docker or OCI format and will be run on Linux x86_64.

Cloud Run is available in all Google Cloud Platform regions globally. If you are
unsure where to deploy to, you can use the
[Region Picker](https://cloud.withgoogle.com/region-picker/) tool to find the
most suitable one. However make sure you select the region where Gemini 2.0 and Imagen 3
are available.

You can configure your project and preferred regions and zones in `gcloud` so
its invocation becomes more convenient.

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region us-central1
gcloud config set artifacts/location us-central1
```

Note that our code is not yet built or containerized, but Cloud Run requires
that. The `gcloud` CLI has a convenient shortcut for deploying Cloud Run which
quickly allows us to do so.

We can use a single command to easily:

- tarball a directory (build context)
- upload it to Cloud Build and use it to untar the context, build the app,
  containerize and store it on Artifact Registry
- create a new Cloud Run service with a fresh revision
- bind an IAM policy to the service
- route traffic to the new endpoint

```bash
cd terraform
terraform init
terraform plan
terraform apply
gcloud run deploy build-your-ai-agent --source .
```

The command requires additional information and hence switches to an interactive
mode. You can have a look at the `gcloud` CLI
[reference](https://cloud.google.com/sdk/gcloud/reference/run/deploy) in case
some of the options may be unclear to you.

We want our application to be publicly available on the internet, so we should
allow unauthenticated invocations from any client.

Wait for the deployment to finish and then navigate to the `*.a.run.app`
endpoint it created. You should be able to call the endpoint from your browser
or by using any other HTTP client like cURL.

Next, let's use `gcloud` to retrieve the auto-generated service URL and then
`curl` it:

```bash
curl $(gcloud run services describe build-your-ai-agent --format 'value(status.url)')
```

Cloud Run services consist of one or more revisions. Whenever you update your
service or its configuration, you are creating a new revision. Revisions are
immutable.

Navigate to the
[Cloud Run section in the Google Cloud Console](https://console.cloud.google.com/run)
to explore the service and its active revision.

Building from `--source` uses Google Cloud Buildpacks. Buildpacks are predefined
archetypes that take your application source code and transform it into
production-ready container images without any additional boilerplate (e.g. a
Dockerfile).
[Learn more about supported languages for Buildpacks](https://cloud.google.com/run/docs/deploying-source-code).

## Using Cloud Code

Alternatively, you can deploy and otherwise manage the life cycle of your Cloud
Run services and other resources using Cloud Code. Cloud Code is an IDE plugin
for both VS Code and Intellj-based IDEs and is designed to make interaction with
Google Cloud more convenient.

Cloud Code is pre-installed in Cloud Shell.

Click the <walkthrough-editor-spotlight spotlightId="activity-bar-cloud-code">
Cloud Code icon in the activity bar </walkthrough-editor-spotlight> to expand
it.

Within the activity bar
<walkthrough-editor-spotlight spotlightId="cloud-code-cloud-run-deploy"> you can
directly deploy to Cloud Run </walkthrough-editor-spotlight> too, without the
need to use the CLI.

Take a moment and familiarize yourself with the wizard. You can also use this
wizard to build and deploy directly to Cloud Run.

**Applications should be engineered to boot quickly.** Cloud Run can start your
containers very quickly, but it is your responsibility to bring up a web server
and you should engineer your code to do so quickly. The earlier this happens,
the earlier Cloud Run is able to route HTTP requests to the new instance, reduce
stress on the older instances and hence scale out effectively. Cloud Run
considers the life cycle stage from starting your application to the moment it
can serve HTTP requests as 'Startup'. During this time Cloud Run will
periodically check if your application has bound the port provided by `$PORT`
and if so, Cloud Run considers startup complete and routes live traffic to the
new instance. Depending on your application code, you can further cut down
startup time by enabling _Startup CPU boost_. When enabled, Cloud Run will
temporarily allocate additional CPU resources during startup of your
application.

**Applications should ideally be stateless.** Cloud Run will also automatically
scale in again, should application traffic decrease. Container instances will be
terminated, if Cloud Run determines that too many are active to deal with the
current request load. When an instance is scheduled for termination, Cloud Run
will change its life cycle stage to 'Shutdown'. You can trap the `SIGTERM`
signal in your code and begin a graceful shutdown of your instance. Requests
will no longer be routed to your container and your application has 10 seconds
to persist data over the network, flush caches or complete some other remaining
write operations.

**Applications are generally request-driven**. During the 'Startup' and
'Shutdown' stages of each container life cycle, your application can expect to
be able to fully use the allocated CPU. During the 'Serving' life cycle, the CPU
is only available when there is at least one active request being processed on a
container instance. If there is no active request on the instance, Cloud Run
will throttle the CPU and use it elsewhere. You will not be charged for CPU time
if it's throttled. Occasionally, you might create applications that require a
CPU to be always available, for instance when running background services. In
this scenario, you want to switch from Cloud Run's default _CPU allocated during
requests_ to the alternative mode _CPU always allocated_. Note that this will
also switch Cloud Run to a
[different pricing model](https://cloud.google.com/run/pricing#tables). The
following diagram shows the two pricing models and their effect on how CPUs are
throttled throughout the life cycle of a container instance.

![Cloud Run container life cycle and CPU throttling](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/lifecycle.png)

Take a look at the deployment wizard for your service in the
[Cloud Run section in the Google Cloud Console](https://console.cloud.google.com/run/deploy/europe-north1/jokes)
and make sure **Startup CPU boost** is enabled.

While you are in the Google Cloud Console, have a look at
[the metrics section of your service](https://console.cloud.google.com/run/detail/europe-north1/jokes/metrics)
and explore how the previously executed load test affected scaling.

## Summary

You now have a good feel for what it means to build and deploy your code to
Cloud Run.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

This completes Module 1. You can now wait for the live session to resume or
continue by yourself and on-demand.

## Module 2: Building and deploying container images with Cloud Build

## Module 3: Building and deploying container images with Cloud Build

![Tutorial header image](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/build.jpg)

In this tutorial we'll learn how to use Cloud Build, the fully-managed CI system
on Google Cloud. Instead of using Build Packs, we'll be using Dockerfiles and
Cloud Builds own declarative configuration to leverage higher flexibility and
control over how we build our images. Finally, we'll use Cloud Build to also
deploy to Cloud Run, so we can continuously deliver updates to our Cloud Run
services.

[Overview on Cloud Build](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/overview-build.png)

<walkthrough-tutorial-difficulty difficulty="3"></walkthrough-tutorial-difficulty>

Estimated time:
<walkthrough-tutorial-duration duration="35"></walkthrough-tutorial-duration>

To get started, click **Start**.

## Project setup

First, let's make sure we got the correct project selected. Go ahead and select
the provided project ID.

<walkthrough-project-setup billing="true"></walkthrough-project-setup>

<walkthrough-enable-apis apis="cloudbuild.googleapis.com,
run.googleapis.com,
artifactregistry.googleapis.com"> </walkthrough-enable-apis>

## Cloud Build

Cloud Build is a fully-managed CI system in Google Cloud. It is a general
purpose compute platform that allows you to execute all sorts of batch
workflows. However, it really excels at building code and creating container
images.

You don't need to provision anything to get started with using Cloud Build, it's
fully-managed: simply enable the API and submit your jobs. Cloud Build manages
all the required infrastructure for you. Per default, Cloud Build schedules
build jobs on shared infrastructure, but it can be configured to run on a
[dedicated worker pool](https://cloud.google.com/build/docs/private-pools/private-pools-overview)
that is not shared with other users.

In the previous section of our journey we saw how to use build and deploy
directly to Cloud Run from source code using the magic of Build Packs. Actually,
this deployment via `gcloud run deploy` already leverages Cloud Build in the
background, as you can see here in the
[Cloud Build History](https://console.cloud.google.com/cloud-build/builds;region=global).
These are great to get you started quickly. Almost as quickly, you will realize
that you need more control over your build process, so you will start writing
your own Dockerfiles. Let's see how that works with Cloud Build.

In order to get started let's set up some configuration:

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region europe-north1
gcloud config set artifacts/location europe-north1
```

We are building some container images in this tutorial, so let's set up a
dedicated Docker image registry using Google Cloud Artifact Registry and
remember it in `gcloud config`:

```bash
gcloud artifacts repositories create my-repo --repository-format docker
gcloud config set artifacts/repository my-repo
```

Great! Let's get started.

## Building with Dockerfiles

Previously, we built our container images by specifying the `--source` flag,
which will cause Cloud Build to use
[Google Cloud Buildpacks](https://cloud.google.com/docs/buildpacks/overview) to
automatically determine the tool chain of our application. It then uses
templated container build instructions which are based on best practices to
build and containerize the application.

Sometimes it is required to exert more control over the Docker build process.
Google Cloud Build also understands Dockerfiles. With Dockerfiles it is possible
to precisely specify which instructions to execute in order to create the
container image. Cloud Build typically inspects the build context and looks for
build instructions in the following order:

1. cloudbuild.yaml: If this file is present, Cloud Build will execute the
   instructions defined in it. We'll learn about cloudbuild.yaml files later in
   this tutorial.
2. Dockerfile: If this file is present, Cloud Build will use it to execute a
   container build process that is equivalent to running `docker build`.
   Finally, it will tag and store the resulting image.
3. Buildpacks: If no explicit build instructions are available, Cloud Build can
   still be used to integrate by using Google Cloud Buildpacks.

In the <walkthrough-editor-spotlight spotlightId="activity-bar-explorer"> File
Explorer </walkthrough-editor-spotlight> create a new file called `Dockerfile`
and place it in the same directory as the Go application. Let's start with a
simple, single-stage build for Go:

```Dockerfile
FROM golang:1.22-bookworm
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -v -o server
CMD ["/app/server"]
```

This Dockerfile:

1. uses Debian bookworm with Golang 1.22 as base image
2. copies the definition of the Go module and installs all dependencies
3. copies the sources and builds the Go application
4. specifies the application binary to run

We can now submit the build context to Cloud Build and use the instructions in
the Dockerfile to create a new image by running:

```bash
LOCATION="$(gcloud config get-value artifacts/location)"
PROJECT="$(gcloud config get-value project)"
gcloud builds submit . \
  --tag ${LOCATION}-docker.pkg.dev/${PROJECT}/my-repo/dockerbuild
```

Next, let's navigate first to the
[Cloud Build History](https://console.cloud.google.com/cloud-build/builds;region=global)
to see the build we just started. As soon as that is finished we go to
[Artifact Registry in the Google cloud Console](https://console.cloud.google.com/artifacts/docker?project=<walkthrough-project-id/>)
to find the repository and inspect the image.

Huh, it seems like our image is quite big! We can fix this by running a
[multi-stage Docker build](https://docs.docker.com/build/building/multi-stage/).
Let's extend the Dockerfile and replace its contents with the following:

```Dockerfile
FROM golang:1.22-bookworm as builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -v -o server

FROM gcr.io/distroless/static-debian11
WORKDIR /app
COPY --from=builder /app/server /app/server
CMD ["/app/server"]
```

Great! We'll keep the first stage as the build stage. Once the statically-linked
Go binary is built, it is copied to a fresh stage that is based on
`gcr.io/distroless/static-debian11`. The _distroless_ images are Google-provided
base images that are very small. That means there is less to store and images
typically have much smaller attack surfaces and improved start-up time. Let's
build again:

```bash
LOCATION="$(gcloud config get-value artifacts/location)"
PROJECT="$(gcloud config get-value project)"
gcloud builds submit . \
  --tag ${LOCATION}-docker.pkg.dev/${PROJECT}/my-repo/dockermultistage
```

Navigate back to Artifact Registry in the Google Cloud Console and inspect the
new image `dockermultistage`. The resulting image is much (70x) smaller.

## Building with a cloudbuild.yaml file

Cloud Build will build, tag and store your container image when you submit a
Dockerfile, but it can do a lot more. You can instruct Cloud Build to execute
any arbitrary sequence of instructions by specifying and submitting a
`cloudbuild.yaml` file. When detected in the build context, this file will take
precedence over any other configuration and will ultimately define what your
Cloud Build task does.

In a nutshell, you are able to specify a sequence of steps with each step being
executed in a container. You can specify which image and process to execute for
every individual step. The steps can collaborate and share data via a shared
volume that is automatically mounted into the file system at `/workspace`.

Go ahead and create a `cloudbuild.yaml` and place it in the same directory as
the Dockerfile and the Go application. Add the following contents:

```yaml
steps:
  - name: "ubuntu"
    args:
      - "echo"
      - "hi there"
```

This configuration asks Cloud Build to run a single step: Use the container
image provided by [ubuntu](https://hub.docker.com/_/ubuntu) and run `echo`.

While this might not be a terribly useful or sophisticated CI pipeline, it is a
useful illustration to understand how versatile Cloud Build is. Let's run it by
submitting a new Cloud Build task:

```bash
gcloud builds submit
```

OK. Let's modify the `cloudbuild.yaml` to do something that's actually useful.
Replace the file contents with the following:

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "build"
      - "-t"
      - "$_ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/my-repo/dockercloudbuildyaml"
      - "."
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "push"
      - "$_ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/my-repo/dockercloudbuildyaml"
```

Pay attention to the `$`-prefixed `$PROJECT_ID` and `$_ARTIFACT_REGION`.
`$PROJECT_ID` is a pseudo-variable which is automatically set by the Cloud Build
environment. `$_ARTIFACT_REGION` is what Cloud Build calls a _substitution_ and
it allows users to override otherwise static content of the build definition by
injecting configuration during invocation of the build. Let's take a look:

```bash
LOCATION="$(gcloud config get-value artifacts/location)"
gcloud builds submit \
  --substitutions _ARTIFACT_REGION=${LOCATION}
```

This will build, tag and store a container image.

To fully understand what else can go into your `cloudbuild.yaml`, please check
out the
[schema documentation](https://cloud.google.com/build/docs/build-config-file-schema).

## Deploying to Cloud Run

Cloud Build is a versatile tool and is suited to run a wide variety of
batch-like jobs. Until now, we only used Cloud Build to accomplish Continuous
Integration (CI) tasks, but we don't need to stop there.

We can extend the `cloudbuild.yaml` definition and automatically deploy the
newly created image to Cloud Run like this:

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "build"
      - "-t"
      - "$_ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/my-repo/dockercloudbuildyaml"
      - "."
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "push"
      - "$_ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/my-repo/dockercloudbuildyaml"
  - name: "gcr.io/cloud-builders/gcloud"
    args:
      - "run"
      - "deploy"
      - "--region"
      - "$_RUN_REGION"
      - "--image"
      - "$_ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/my-repo/dockercloudbuildyaml"
      - "jokes"
```

In order for this to work, we need to grant some permissions to the service
account used by the Cloud Build service agent, so it can interact with Cloud Run
resources on our behalf.

Navigate to the
[settings section of Cloud Build in the Google Cloud Console](https://console.cloud.google.com/cloud-build/settings/service-account)
and assign both the **Cloud Run Admin** and the **Service Account User** roles
to Cloud Build's service account.

Finally, let's supply all the substitutions and invoke Cloud Build once again to
execute a fresh build and deploy to Cloud Run automatically.

```bash
LOCATION="$(gcloud config get-value artifacts/location)"
REGION="$(gcloud config get-value run/region)"
gcloud builds submit \
  --substitutions _ARTIFACT_REGION=${LOCATION},_RUN_REGION=${REGION}
```

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

This completes Module 3. You can now wait for the live session to resume or
continue by yourself and on-demand.

<walkthrough-inline-feedback></walkthrough-inline-feedback>
