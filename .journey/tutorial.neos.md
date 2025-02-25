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

**Module 1** will explore Cloud Run, a compute platform for container workloads,
which you can use to easily run your services in a scalable, secure,
cost-effective and production-grade environment in a matter of minutes.

**Module 2** will explore Gemini's Function Calling feature. We will add new
 methods to fetch data from Firestore and manipulate your character 3D models a little bit.

**Module 3** will show you how to work with RAG (Retrieval Augmented Generation). 
in Vertex AI with help of our Python SDK.

**Module 4** will let you showcase what you learned and make the Meow AI Agent create 
a 3D model based on your avatar! 

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

gcloud storage buckets create gs://build-you-ai-agent-$(gcloud projects list --filter PROJECT_ID=<walkthrough-project-id/> --format="value(PROJECT_NUMBER)") --location=us-central1
gsutil cp -r data/* gs://build-you-ai-agent-$(gcloud projects list --filter PROJECT_ID=<walkthrough-project-id/> --format="value(PROJECT_NUMBER)")

gcloud firestore import gs://build-you-ai-agent-$(gcloud projects list --filter PROJECT_ID=<walkthrough-project-id/> --format="value(PROJECT_NUMBER)")/firestore-data --database="(default)"
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
most suitable one. However make sure you select the region where Gemini 2.0, Imagen 3
and RAG Engine API are available, hence for this demo we suggest using us-central1.

You can configure your project and preferred regions and zones in `gcloud` so
its invocation becomes more convenient.

```bash
gcloud config set project <walkthrough-project-id/>
gcloud config set run/region us-central1
gcloud config set artifacts/location us-central1
```

First we need to setup all the bits and pieces for our service to work. For that we
use terraform that has already been configured to create a Cloud Run dummy service,
Artifact Registry and all the necessary permissions. Run the following commands to 
do just that:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Now with that out of the way, we need to focus on our code that is not yet built 
nor containerized, but Cloud Run requires that. The `gcloud` CLI has a convenient 
shortcut for deploying Cloud Run which quickly allows us to do so.

We can use a single command to easily:

- tarball a directory (build context)
- upload it to Cloud Build and use it to untar the context, build the app,
  containerize and store it on Artifact Registry
- create a new Cloud Run service with a fresh revision
- bind an IAM policy to the service
- route traffic to the new endpoint

```bash
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

## Module 2: 

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

This completes Module 2. You can now wait for the live session to resume or
continue by yourself and on-demand.

## Module 3: 

This completes Module 3. You can now wait for the live session to resume or
continue by yourself and on-demand.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

## Module 4: 

This completes Module 4. You can now wait for the live session to resume or
continue by yourself and on-demand.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

You have completed the tutorial, well done! Please take a moment and let us know
what you think.

<walkthrough-inline-feedback></walkthrough-inline-feedback>
