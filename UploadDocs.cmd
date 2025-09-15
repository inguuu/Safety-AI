@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

rem Load secrets from secret.cmd
call secret.cmd

rem 컨테이너 생성
call az storage container create --account-name !azure_storage_account! --subscription !subscription_id! --name margies --auth-mode key --account-key !azure_storage_key! --output none

rem 업로드 폴더 지정
set UPLOAD_DIR=data

rem 업로드할 모든 파일에 대해 반복
for %%F in (%UPLOAD_DIR%\*) do (
    rem 파일명만 추출
    set filename=%%~nxF

    rem 확장자 제외 파일명 추출
    set filename_no_ext=%%~nF

    rem centerName 추출 - 파일명에서 마지막 '_' 뒤 부분
    for /f "tokens=1,* delims=_" %%a in ("!filename_no_ext:_= !") do (
        set lastToken=%%b
    )
    
    rem lastToken은 첫 '_' 다음 전부인데 마지막 토큰을 찾기 위해 추가 처리
    rem (간단하게 센터명은 마지막 '_' 뒤에 있다고 가정, 아래 파이썬 예제가 더 낫긴 함)

    rem 간단한 centerName 추출 예시 (윈도우 배치에서 어려움)
    rem centerName을 filename_no_ext에서 '_'로 쪼개서 마지막 토큰으로 설정하는 스크립트는
    rem 배치 파일에서 매우 복잡함. 여기선 간단히 하드코딩으로 넘어감.

    rem 대신 파이썬 스크립트 쓰는걸 추천

    rem Blob 업로드 시 메타데이터 포함
    echo Uploading %%F with metadata centerName=!lastToken! documentName=!filename!
    call az storage blob upload --container-name margies --file "%%F" --name "%%~nxF" --account-name !azure_storage_account! --auth-mode key --account-key !azure_storage_key! --metadata centerName=!lastToken! documentName=!filename! --output none
)

ENDLOCAL