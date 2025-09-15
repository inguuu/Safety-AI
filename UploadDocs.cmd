rem UploadDocs.cmd 터미널 입력

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

rem Load secrets from secret.cmd (이 파일은 gitignore)
call secret.cmd

echo Creating container...
call az storage container create --account-name !azure_storage_account! --subscription !subscription_id! --name margies --auth-mode key --account-key !azure_storage_key! --output none

echo Uploading files...
call az storage blob upload-batch -d margies -s data --account-name !azure_storage_account! --auth-mode key --account-key !azure_storage_key!  --output none
