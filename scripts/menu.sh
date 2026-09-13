#!/bin/bash
clear
echo "=========================================="
echo " 🎮 SURVIVAL RPG - TERMUX CONTROL CENTER  "
echo "=========================================="
echo " 1. 🐙 Push Latest Changes to GitHub"
echo " 2. 🔥 Open Firebase Projects"
echo " 3. 📱 Check GitHub Repository Status"
echo " 4. ❌ Exit"
echo "=========================================="
read -p "Select [1-4]: " choice
case $choice in
  1)
    git add .
    read -p "Enter commit message: " msg
    git commit -m "$msg"
    git push origin main
    echo "✅ Pushed to GitHub!"
    ;;
  2)
    firebase projects:list
    ;;
  3)
    gh repo view --web || echo "Repo: https://github.com/meenafulzele077-svg/survival-rpg-game"
    ;;
  4)
    exit 0
    ;;
esac
