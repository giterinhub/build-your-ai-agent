<!--markdownlint-disable MD024 MD033 MD036 MD041 -->
<walkthrough-metadata>
  <meta name="title" content="Google Cloud Platform" />
  <meta name="description" content="Learn how to build and run containerized
  services, use automated build and deployment tools, implement Google Cloud
  APIs to leverage GenAI capabilities and operate your service in production
  ." />
  <meta name="keywords" content="cloud, go, containers, console, run, AI,
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
 methods to fetch data from AlloyDB and manipulate 3D models a little bit.

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
alloydb.googleapis.com,
artifactregistry.googleapis.com"> </walkthrough-enable-apis>

You can use the builtin
<walkthrough-editor-spotlight spotlightId="menu-terminal-new-terminal"> Cloud
Shell Terminal </walkthrough-editor-spotlight> to run the gcloud command.

## Exploring the code

Take some time and
<walkthrough-editor-open-file filePath="cloudshell_open/serverless/main.go">
familiarize yourself with the code. </walkthrough-editor-open-file>

Also have a look at the dependencies reference in the Go module. You can
navigate to its [upstream repository](https://github.com/NucleusEngineering/build-your-ai-agent)
to figure out what it does.

Once you've understood what's going on, you can try to run that app directly in
Cloud Shell, running the following in the terminal:

```bash
docker compose up
```

This downloads dependencies, compiles and starts the web server. You can now use
Cloud Shell Web Preview on port 8080 to check out your application. You can find
the Web Preview <walkthrough-web-preview-icon></walkthrough-web-preview-icon> at
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
most suitable one.

You can configure your project and preferred regions and zones in `gcloud` so
its invocation becomes more convenient.

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region europe-north1
gcloud config set artifacts/location europe-north1
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
gcloud run deploy jokes --source .
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
curl $(gcloud run services describe jokes --format 'value(status.url)')
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

## Scaling your app

Cloud Run automatically scales your application based on how many web requests
are coming in via the HTTPS endpoint. Cloud Run's horizontal auto-scaler is
extremely fast and can launch 100s of new instances in seconds.

Let's put some load on our newly created service and learn about scaling while
we wait. We'll start by pushing 50.000 requests using `hey`:

```bash
hey -n 50000 $(gcloud run services describe jokes --format 'value(status.url)')
```

In order to build modern, cloud-first applications that scale well horizontally,
we need to watch out for some design considerations.

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

## Setting up an automatic source triggers from GitHub

Now that we have successfully created a full build definition on Cloud Build for
a simple yet very useful CI/CD pipeline, let's have a look at creating automatic
build triggers that execute the pipeline whenever code gets updated on a remote
Git repository. In order to put everything in place, we'll now look at how to
authenticate with GitHub, fork the code into a new repository, authorize GitHub
to connect with Cloud Build and create an automatic build trigger on Cloud
Build.

<walkthrough-info-message>This part of the tutorial is **optional**, as it
requires you to have a GitHub account. If you don't have one you can
[register a new one](https://github.com/signup).</walkthrough-info-message>

### Authenticating with GitHub

First, let's authenticate using `gh`, GitHub's CLI, which comes pre-installed on
Cloud Shell. In your terminal begin the authentication handshake and complete
the CLI wizard.

We'd like to connect in the following matter:

- Connect to `github.com`
- Use HTTPS for authentication
- Configure `git` to use GitHub credentials

Begin the authentication exchange by running the following:

```bash
gh auth login
```

Copy the authentication code, navigate to
[GitHub's device authentication page](https://github.com/login/device), paste
the token and authorize the application.

Once authentication is complete, you should be able to test access to GitHub by
listing all of your repositories, like so:

```bash
gh repo list
```

### Creating a fork of the upstream repo

Next, we'll create a fork of the repository we are currently working with, so
that we have a separate, remote repository that we can push changes to. Create
the fork by running the following:

```bash
gh repo fork
```

This will create a fork of the upstream repository from
`github.com/nucleusengineering/serverless` and place it at
`github.com/YOUR_GITHUB_HANDLE/serverless`. Additionally, the command
automatically reconfigures the remotes of the local repository clone. Take a
look the the configured remotes and see how it configured both `upstream` and
the new `origin` by running the following:

```bash
git remote -v
```

<walkthrough-info-message>Make sure that your new `origin` points to the work
belonging to your own user and push commits to the new `origin` from now
on.</walkthrough-info-message>

### Setting up the Cloud Build triggers

Next, Cloud Build needs to be configured with a trigger resource. The trigger
contains everything Cloud Build needs to automatically run new builds whenever
the remote repository gets updated.

- Navigate to the
  [Cloud Build triggers section of the Google Cloud Console](https://console.cloud.google.com/cloud-build/triggers)
  and click on 'Connect Repository'.
- Follow the wizard on the right to connect to github.com, authenticate Google's
  GitHub app.
- Filter repositories based on your user name.
- Find the forked repository called 'serverless'.
- Tick the box to accept the policy and connect your repository.

Once completed you should see a connection confirmation message displayed. Now
it's time to create the trigger.

- Hit 'Create Trigger' and create a new trigger.
- In the wizard, specify that the trigger should read configuration from the
  provided `./cloudbuild.yaml` and **add all the substitutions** you used
  previously to trigger your build.

<walkthrough-info-message>When using the "Autodetect" configuration option,
there is no possibility to add substitution variables through the UI. So make
sure to specify the "Cloud Build configuration file (yaml or json)" option
explicitly, and then continue to fill in the substitution
variables.</walkthrough-info-message>

### Pushing some changes

We should now have everything in place to automatically trigger a new build
whenever changes are pushed to `main` on the remote repository fork.

If you haven't done so already, you will need to configure git on your Cloud
Shell. To do so, run the following and configure your email and name, so git
know who you are.

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

Use git to add all the changes to the index and create a commit like this:

```bash
git add Dockerfile
git add cloudbuild.yaml
git commit -m 'add build config'
```

Finally, push the commit to the remote repository:

```bash
git push origin main
```

Changes should automatically be detected and trigger a new Cloud Build task.
Navigate to the
[Cloud Build dashboard](https://console.cloud.google.com/cloud-build/dashboard)
and explore the running build.

## Summary

You now know how Cloud Build can help you automate integrating your artifacts.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

This completes Module 2. You can now wait for the live session to resume or
continue by yourself and on-demand.

## Module 3: Extend your code to call Cloud APIs

![Tutorial header image](https://raw.githubusercontent.com/NucleusEngineering/serverless/main/.images/apis.jpg)

In this tutorial we'll learn how to extend the existing code to call Cloud APIs
directly. Currently, the deployed application uses a library which contains a
static set of jokes. Whenever the library is used it randomly selects a joke and
returns it. After a while we will surely start to see the same jokes again and
the only way to see new jokes is when a human would actually implement them in
the library.

Luckily, there is a thing called _generative AI_ now. Google Cloud Vertex AI
contains the Google-built, pre-trained, Gemini 1.5 Flash model which is a
general-purpose, multimodal, speed-optimized, generative large language model
(LLM) that can be queried with text prompts in natural language to generate all
sorts of outputs, including text. In this tutorial we'll implement the
`model:predict` endpoint of Vertex AI to execute this model in order to add new
dad jokes in a generative manner.

<!-- TODO: include on-demand clip for module 3 -->

Additionally, we'll learn a little bit about custom service accounts, IAM
permissions and how to use the principle of least privilege to secure our
services on Cloud Run.

<walkthrough-tutorial-difficulty difficulty="3"></walkthrough-tutorial-difficulty>

Estimated time:
<walkthrough-tutorial-duration duration="45"></walkthrough-tutorial-duration>

To get started, click **Start**.

## Project setup

First, let's make sure we got the correct project selected. Go ahead and select
the provided project ID.

<walkthrough-project-setup billing="true"></walkthrough-project-setup>

Run the following to make sure all required APIs are enabled. Note that
`aiplatform.googleapis.com` is added.

<walkthrough-enable-apis apis="cloudbuild.googleapis.com,
run.googleapis.com,aiplatform.googleapis.com,
artifactregistry.googleapis.com"> </walkthrough-enable-apis>

## About the different ways to call Google APIs

In the cloud we often need to implement API calls to interact with other
services. Platforms like Google Cloud are a large collection of APIs; if we
learn how to use them we can use the entire wealth of Google Cloud's
functionality in our applications and build almost anything!

There are typically three different ways to interact with Google APIs
programmatically and we should choose them in the following order:

1. **Cloud Client Libraries**: These are the recommended options. Cloud Client
   Libraries are SDK that you can use in a language-native, idiomatic style.
   They give you a high-level interface to the most important operation and
   allow you to quickly and comfortably get the job done. An example in the Go
   ecosystem would be the `cloud.google.com/go/storage` package, which
   implements the most commonly used operations of Google Cloud Storage. Have a
   look at the
   [documentation of the package](https://pkg.go.dev/cloud.google.com/go/storage)
   and see how it respects and implements native language concepts like the
   `io.Writer` interface of the Go programming language.

2. **Google API Client Libraries**: Should no Cloud Client Library be available
   for what you are trying to accomplish you can fall back to using a Google API
   Client Library. These libraries are auto-generated and should be available
   for almost all Google APIs.

3. **Direct Implementation**: You can always choose to implement exposed APIs
   directly with your own client code. While most APIs are available as
   traditional RESTful services communicating JSON-serialized data, some APIs
   also implement [gRPC](https://grpc.io).

Have a look at
[this page of the Google Cloud documentation](https://cloud.google.com/apis/docs/client-libraries-explained)
to learn more about the differences between the available libraries.

Let's configure `gcloud` for the project and default regions:

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region europe-north1
gcloud config set artifacts/location europe-north1
```

Okay, all set!

## Extending the code

In order to be able to replace the statically created jokes with jokes generated
by Vertex AI, the code needs to be extended in the following ways:

1. **Create a client to execute the remote model**: The first step is to safely
   instantiate the correct client type, that we are going to use later on to
   interact with the API. This type holds all the configuration for endpoints
   and handles authentication, too. Have a look at the
   [documentation of the package](https://pkg.go.dev/cloud.google.com/go/vertexai/genai#NewClient)
   for `genai.Client`. The client will automatically look for credentials
   according to the rules of
   [Google's Application Default Credentials scheme](https://cloud.google.com/docs/authentication/application-default-credentials).

2. **Execute the call against the API to run the model prediction**: Next, we'll
   use the previously instantiated client to actually invoke the remote model
   with `[]genai.Parts` containing the prompt and execute the API by calling
   `genai.GenerateContent`
   [as described in the docs](https://pkg.go.dev/cloud.google.com/go/vertexai/genai#GenerativeModel.GenerateContent).
   Take a look at the
   [documentation of the package](https://pkg.go.dev/cloud.google.com/go/vertexai/genai#GenerativeModel)
   to see what else can be done with `genai.GenerativeModel`.

Now, it's time to make some changes to the code.

<walkthrough-info-message>You may now attempt to **implement the above code
changes yourself** for which you should have a good understanding of the Go
programming language. If you choose to do so, you should stop reading now and
give it your best shot.</walkthrough-info-message>

Alternatively, you can **use a prebuilt library** to accomplish the same. If
that's more your cup of tea, go hit 'Next' and proceed to the next section.

Have a look at the
[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemini-1.5-flash-preview-0514)
to learn more about Gemini Flash and other available models.

## Using a library to call the Gemini Flash model

To get started, first have a look at the Go module
`github.com/helloworlddan/tortuneai`. The module provides the package
`github.com/helloworlddan/tortuneai/tortuneai` which implements the Cloud Client
Library for Vertex AI to call the _Gemini Flash_ model.
[Read through the code](https://github.com/helloworlddan/tortuneai/blob/main/tortuneai/tortuneai.go)
of `tortuneai.HitMe` and see how it implements the aforementioned steps to
interact with the API.

In order to use the package we need to first get the module like this:

```bash
go get github.com/helloworlddan/tortuneai@v0.0.4
```

Once that is completed, we can update
<walkthrough-editor-open-file filePath="cloudshell_open/serverless/main.go"> the
main application source file main.go </walkthrough-editor-open-file> and change
all references to the previously used package `tortune` with `tortuneai`.

Notice that the signature for `tortuneai.HitMe()` is different from the previous
`tortune.HitMe()`. While the original function did not require any parameters,
you are required to pass two `string` values into the new one: One with an
actual text prompt for the Gemini Flash model and one with your Google Cloud
project ID. Additionally, the function now returns multiple return values: a
`string` containing the response from the API and an `error`. If everything goes
well, the error will be `nil`, if not it will contain information about what
went wrong.

Here is a possible implementation:

```golang
joke, err := tortuneai.HitMe("", "<walkthrough-project-id/>")
if err != nil {
    fmt.Fprintf(w, "error: %v\n", err)
    return
}
fmt.Fprint(w, joke)
```

Update the implementation of `http.HandleFunc()` in
<walkthrough-editor-open-file filePath="cloudshell_open/serverless/main.go"> the
main application source file main.go </walkthrough-editor-open-file> with the
code snippet.

Let's check if the modified code compiles by running it:

```bash
go run main.go
```

This recompiles and starts the web server. Let's check the application with the
Web Preview <walkthrough-web-preview-icon></walkthrough-web-preview-icon> at the
top right in Cloud Shell and see if we can successfully interact with the Gemini
Flash model.

If you are satisfied you can focus the terminal again and terminate the web
server with `Ctrl-C`.

It's good practice to clean up old dependencies from the `go.mod` file. You can
do this automatically my running:

```bash
go mod tidy
```

If you like you can stay at this point for a moment, change the prompt (the
first argument to `tortuneai.HitMe()`), re-run with `go run main.go` and use the
Web Preview <walkthrough-web-preview-icon></walkthrough-web-preview-icon> to
have a look at how the change in prompt affected the model's output.

## Creating a custom service account for the Cloud Run service

Good! The code changes we made seem to work, now it's time to deploy the changes
to the cloud.

When running the code from Cloud Shell, the underlying implementation used
Google
[Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/provide-credentials-adc)
to find credentials. In this case it was using the credentials of the Cloud
Shell user identity (yours).

Cloud Run can be configured to use a service account, which exposes credentials
to the code running in your container. Your application can then make
authenticated requests against Google APIs.

Per default, Cloud Run uses the
[Compute Engine default service account](https://cloud.google.com/compute/docs/access/service-accounts#default_service_account).
This service account has wide permissions and should generally be replaced by a
service account with the least amount of permissions required to do whatever
your service needs to do. The Compute Engine default service has a lot of
permissions, but it does not have the required permissions to execute
[the API call](https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/projects.locations.publishers.models/predict).

When it comes to identifying the correct IAM roles to attach to identities
[this reference page on the IAM documentation](https://cloud.google.com/iam/docs/understanding-roles)
is an extremely useful resource. On the page you can check the section for
[Vertex AI roles](https://cloud.google.com/iam/docs/understanding-roles#vertex-ai-roles)
and learn that
[_Vertex AI User_](https://cloud.google.com/iam/docs/understanding-roles#aiplatform.user)
(`roles/aiplatform.user`) is a suitable role for our Cloud Run service, because
this role contains the permission `aiplatform.endpoints.predict`. If you are
unsure which permission you require, you can always check the
[API reference for the required operation](https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/projects.locations.publishers.models/predict).

<walkthrough-info-message>**Note**: You could argue that the role _Vertex AI
User_ has too many permissions for the Cloud Run service and a
security-conscious person would probably agree with you. If you really wanted to
make sure that the Cloud Run service only had least amount of privilege to
execute the absolutely required permissions, you would have to create a
[IAM custom role](https://cloud.google.com/iam/docs/creating-custom-roles) to
achieve this.</walkthrough-info-message>

For now, we'll stick with _Vertex AI User_.

Next, let's create a brand new customer IAM service account like this:

```bash
gcloud iam service-accounts create tortune
```

We can bind the identified role to the various resource levels. For the sake of
simplicity, let's attach it at the project level by executing:

```bash
PROJECT=$(gcloud config get-value project)
ACCOUNT=tortune@${PROJECT}.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${ACCOUNT} \
    --role "roles/aiplatform.user"
```

The service account will now be able to use all the permissions in _Vertex AI
User_ on all resources in our current project. Finally, we need to deploy a new
Cloud Run revision by updating the service configuration so that our Cloud Run
service will use the newly-created service account:

```bash
PROJECT=$(gcloud config get-value project)
ACCOUNT=tortune@${PROJECT}.iam.gserviceaccount.com
gcloud run services update jokes \
    --service-account ${ACCOUNT}
```

Now, that all IAM resources and configurations are in place, we can trigger a
new Cloud Build execution to deploy changes in a CI/CD fashion, like this:

```bash
LOCATION="$(gcloud config get-value artifacts/location)"
REGION="$(gcloud config get-value run/region)"
gcloud builds submit \
  --substitutions _ARTIFACT_REGION=${LOCATION},_RUN_REGION=${REGION}
```

If you have previously configured Github, you can achieve the same by committing
and pushing your changes, like this:

```bash
git add .
git commit -m 'upgrade to Gemini Flash for generative jokes'
git push origin main
```

Navigate to
[Cloud Build's dashboard](https://console.cloud.google.com/cloud-build/dashboard)
and click into the active build to monitor it's progress.

Once completed, you should be able to get fresh generated content by cURLing the
endpoint of the Cloud Run Service:

```bash
curl $(gcloud run services describe jokes --format 'value(status.url)')
```

Amazing!

## Summary

You now know how to call Google APIs directly from your code and understand how
to secure your services with least-privilege service accounts.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

This completes Module 3. You can now wait for the live session to resume or
continue by yourself and on-demand.

<walkthrough-inline-feedback></walkthrough-inline-feedback>
