# Infrastructure as Code - Sample Project 

<div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0;">

  <div style="flex: 1; text-align: center; margin: 0 10px;">
    <a href="https://github.com/localstack/localstack" target="_blank" rel="noopener noreferrer">
      <img src="https://avatars.githubusercontent.com/u/28732122?s=48&v=4"
           alt="LocalStack logo"
           style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
    </a>
    <div style="font-size: 0.9em; margin-top: 6px;">LocalStack</div>
  </div>

  <div style="flex: 1; text-align: center; margin: 0 10px;">
    <a href="https://aws.amazon.com/" target="_blank" rel="noopener noreferrer">
      <img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg"
           alt="AWS logo"
           style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
    </a>
    <div style="font-size: 0.9em; margin-top: 6px;">Amazon Web Services</div>
  </div>

  <div style="flex: 1; text-align: center; margin: 0 10px;">
    <a href="https://www.python.org/" target="_blank" rel="noopener noreferrer">
      <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg"
           alt="Python logo"
           style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
    </a>
    <div style="font-size: 0.9em; margin-top: 6px;">Python</div>
  </div>

</div>



## 🛠️ Setup Development (Windows)

### 🔧 1. Install Dependencies
1. 🐧 Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) --  Run the following in a **new PowerShell terminal**
```powershell
    wsl --install
```
2. 📦 Install [Scoop](https://scoop.sh/)-- Check website for latest version/instructions --  Run the following in a **new PowerShell terminal**
```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```
3. 🌱 Install [Git](https://git-scm.com/downloads/win)
```powershell
scoop install git
```
4. 📝 Install [VSCode](https://code.visualstudio.com/docs/?dv=win64user)
```powershell
scoop bucket add extras
scoop install vscode
```
5. 🐳 Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
6. 🐍 Install Python
```powershell
scoop install python
```
7. ⚡Install [.NET 8 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/sdk-8.0.414-windows-x64-installer)

8. Install `infra-lib` CLI
```powershell
https://github.com/y3rbiadit0/infra_lib/tree/main
```

## Key Concepts

This example shows the benefits of IaC:

- **Automated Infrastructure**: All AWS resources (Lambda, API Gateway, Secrets Manager) are provisioned through code, no manual clicks in the console.
- **Reproducibility**: Deploy the same environment locally or in the cloud, consistently.
- **Versioning**: Infrastructure definitions can live alongside your application code in Git.
- **Testability**: LocalStack allows full local testing of your AWS stack before production deployment.

---

## Infrastructure as Code (IaC) - `infrastructure/`
- **Env variables** (`infrastructure/<environment>/.env`):
  Each environment folder has the environment variables to use when launching the environment.  

- **IaC - Code** (`infrastructure/<environment>/infra_<environment>.py`):  
  Automates LocalStack deployment, Lambda creation, API Gateway setup, Secrets creation. (Describes IaC for each environment)
  
- **Docker Compose** (`infrastructure/docker-compose.yml`):  
  Defines containers for LocalStack, Debugger container, networking, and environment variables.

- **Dockerfile.debug**:  
  Builds the Lambda container for local debugging.

- **localstack_lib**:  
  Core IaC logic to create secrets, Lambda functions, and API Gateway endpoints programmatically.

> ✅ Everything that would normally be manual in AWS is now fully automated and versioned.

---

## Run Project

1. Run -> `infra-cli.exe run --project . --environment "local"` -- Will start a:
   1. `Localstack`
   2. `Local server` being able to do requests to the lambda function
   3. `Debugger Server` to debug the project.
3. Run -> `infra-cli.exe run --project . --environment "local"` -- Will start a:
   1. `Localstack` with `Lambda Functions` deployed as `.zip`

