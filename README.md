![image](https://github.com/user-attachments/assets/b90884b8-acde-4c51-a576-f87503218edf)


Essential Inputs Required for proper configuration and execution : 
| **Input/Configuration**             | **Description**                                      | **Type**               | **Example/Format**                |
|-------------------------------------|------------------------------------------------------|------------------------|------------------------------------|
| **Scripts Folder Location (Local Mount)** | Path to locally mount the scripts directory.        | File Path             | `/home/user/scripts`              |
| **NVD API-KEY**                     | API key for accessing National Vulnerability Database (NVD). | API Key (String)     | `12345-abcd-67890-xyz`            |
| **GitHub Personal Access Token (PAT)** | Token for accessing the GitHub repository securely. | Secret Key (String)   | `ghp_xxx123abc456...`             |
| **Target Folder for Repo Cloning**  | Path to clone the latest GitHub repository locally.  | File Path             | `/home/user/repo_clone`           |
| **Central Security Results Storage Folder** | Path to store aggregated security scan results locally. | File Path         | `/home/user/security_results`     |


Workflow : 
![image](https://github.com/user-attachments/assets/80bb11f2-6604-4ddf-b7c4-f33f65196159)

Pre-Requisites:

- Active Internet Connection
- Target Repositosry's PAT
- Docker Daemon Running 
- Python Configured and Installed
- NVD API Key for SCA 

How to Run : 
- Run the DevSecOpsOTG.py in your terminal. 
- On the Mount Scripts Prompt: Create an Independent Mount Scripts Folder for - master_script.py Script and supply that allied File Path.

You are all Set to Implement Your Localized DevSecOps Pipeline! Hassle-Free. 
