@echo off
echo =======================================================
echo   PUSH TO GITHUB FOR VERCEL DEPLOYMENT
echo =======================================================
echo.

set /p REPO_URL="Apne GitHub Repo ka URL enter karein (e.g. https://github.com/username/waste-ai.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL khali nahi ho sakta.
    pause
    exit /b 1
)

echo.
echo [1/4] Git Initialize ho raha hai...
git init
git branch -M main

echo.
echo [2/4] Files add aur commit ho rahi hain...
git add .
git commit -m "Deploy AI Waste Intelligence System to Vercel"

echo.
echo [3/4] GitHub remote link set ho raha hai...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo.
echo [4/4] GitHub par push ho raha hai...
git push -u origin main

echo.
echo =======================================================
echo   SUCCESS! Ab vercel.com par jakar repo import karein.
echo =======================================================
pause
