@echo off
cd /d "%~dp0"
title �俧�� ColdBrew Hub

rem ==== �����������õ� Python���ų�΢���̵��ռλ�� ====
set "PY="
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY=py -3"
)

if defined PY goto tkcheck

echo [����] δ�ҵ����õ� Python 3.10 ����߰汾
echo.
echo ����취����ѡ��һ����
echo   1. �� https://www.python.org/downloads/ ���ذ�װ Python 3.10+��
echo      ��װʱ��ع�ѡ "Add python.exe to PATH"��
echo   2. ����Ѿ�װ�� Python �Ա�������������΢���̵��
echo      �� Python ռλ�ڵ��ң��� ���� - Ӧ�� - �߼�Ӧ������ -
echo      Ӧ��ִ�б������� python.exe �� python3.exe �Ŀ��عص���
echo.
echo �޺ú�����˫�����ļ����ɡ�
echo.
pause
exit /b 1

:tkcheck
%PY% -c "import tkinter" >nul 2>nul
if not errorlevel 1 goto run

echo [����] Python ȱ�� tkinter��Tcl/Tk ���δ��װ��
echo.
echo ����취���������� Python ��װ����ѡ Modify ��
echo �� Optional Features �ﹴѡ "tcl/tk and IDLE" ��ɰ�װ��
echo ����ֱ��ȥ python.org ��װһ�� Python��Ĭ�ϼ��� tkinter����
echo.
echo �޺ú�����˫�����ļ����ɡ�
echo.
pause
exit /b 1

:run
echo Launching ColdBrew Hub v9 FiveEdge...
%PY% coldbrew_hub.py 2>"�������������־.txt"
if not errorlevel 1 exit /b 0

echo.
echo [����ʧ��] ����쳣�˳�����ϸ������д�뱾Ŀ¼�� "�������������־.txt"��
echo ����־���ݷ����俧������ QQ Ⱥ��1057540028 / 1077074552���ɿ��ٶ�λ��
echo.
pause
exit /b 1
