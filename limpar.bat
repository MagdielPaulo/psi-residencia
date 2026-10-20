@echo off
chcp 65001 >nul
title Limpar Psi Residencia
cd /d "%~dp0"
echo.
echo === Limpando a pasta e atualizando o GitHub ===
echo.
del /q "enviar-para-github.bat" "commit-msg.txt" 2>nul
git rm -q --ignore-unmatch "LEIA-ME.txt"
if exist "LEIA-ME.txt" del /q "LEIA-ME.txt"
git add -A -- . ":!limpar.bat" ":!msg-limpeza.txt"
git commit -q -F "msg-limpeza.txt"
git push
if errorlevel 1 (
  echo.
  echo [ERRO] O envio falhou. Copie a mensagem acima e mande para o Claude.
  pause
  exit /b 1
)
del /q "msg-limpeza.txt" 2>nul
echo.
echo === Pronto! Pasta limpa e GitHub atualizado. Esta janela pode ser fechada. ===
pause
(goto) 2>nul & del "%~f0"
