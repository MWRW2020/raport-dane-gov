#!/bin/bash

# Ustawienie ścieżki do katalogu projektu
PROJECT_DIR="/home/MWRW/raport-dane-gov" # ZMIEŃ NA SWOJĄ NAZWĘ UŻYTKOWNIKA!
VENV_DIR="$PROJECT_DIR/venv"

# 1. Przejdź do katalogu projektu
cd "$PROJECT_DIR" || exit 1

# 2. Aktywuj środowisko wirtualne
source "$VENV_DIR/bin/activate"

# 3. Uruchom skrypt generujący pliki (XML, MD5 i historię)
echo "Uruchamiam generator..."
python generator_danych_gov.py

# 4. Sprawdź, czy są zmiany do skommitowania
if [[ $(git status --porcelain) ]]; then

  echo "Wykryto zmiany. Commituję i pushuję."

  # 5. Dodaj pliki do Git
  git add raport_cen_mieszkan.xml raport_cen_mieszkan.md5 history_dates.txt

  # 6. Utwórz commit z datą i godziną
  COMMIT_MESSAGE="Automat: Aktualizacja danych na $(date +'%Y-%m-%d %H:%M:%S')"
  git commit -m "$COMMIT_MESSAGE"

  # 7. Wypchnij zmiany do GitHub
  # Użycie git pull --rebase i git push jest kluczowe w cronjob
  git pull --rebase origin main
  git push origin main

  echo "Zakończono pomyślnie."
else
  echo "Brak zmian w plikach XML/MD5/Historii. Nie commituję."
fi