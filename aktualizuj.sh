#!/bin/bash

echo "--- 1. Pobieranie zmian z GitHub ---"
git pull origin main

echo "--- 2. Generowanie poprawionego raportu XML (Namespace Fix) ---"
python generator_danych_gov.py

echo "--- 3. Wysyłanie poprawki na GitHub ---"
git add .
git commit -m "FIX: Usunięcie przestrzeni nazw z elementów potomnych zgodnie z wzorcem"
git push origin main

echo "--- GOTOWE! Poprawiony plik jest już na GitHubie ---"
