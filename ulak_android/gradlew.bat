@rem Gradle startup script for Windows

@if "%DEBUG%" == "" @echo off
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

set GRADLE_USER_HOME=%APP_HOME%\gradle

"%APP_HOME%\gradle\wrapper\gradle-wrapper.jar" %*
