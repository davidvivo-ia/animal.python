@echo off
rem ANIMAL — lanzador para Windows.
rem
rem Doble clic, o `scripts\animal.bat --demo --seed 42` desde cmd.exe.
rem Usa uv si está en el PATH; en su defecto cae a `py -m animal`.
rem
rem Para que el doble clic no cierre la ventana al terminar, el ultimo
rem `pause` deja la consola abierta hasta que el jugador pulse una tecla.

setlocal
chcp 65001 >nul

pushd "%~dp0\.."

where uv >nul 2>&1
if %ERRORLEVEL%==0 (
    uv run animal %*
    set EXITCODE=%ERRORLEVEL%
) else (
    where py >nul 2>&1
    if %ERRORLEVEL%==0 (
        py -3.13 -m animal %*
        set EXITCODE=%ERRORLEVEL%
    ) else (
        echo No encuentro ni uv ni py.
        echo Instala uv desde https://docs.astral.sh/uv/
        echo o Python 3.13+ desde https://www.python.org/
        set EXITCODE=1
    )
)

popd

if "%~1"=="" pause
exit /b %EXITCODE%
