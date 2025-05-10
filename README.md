# Code the Future 2025

Echipa - CONA IT Solutions

Membrii echipei:

- OLTEANU Cristian-Alin-Claudiu
- ONOSE Victor Ovidiu
- PRODAN Cosmin Daniel

# Descrierea proiectului

Aceasta este o aplicatie de tip E-commerce unde utilizatorii pot achizitiona cuburi de lemn de diferite culori. La fiecare comanda de cuburi stocul acestora este actualizat in baza de date. De asemenea, am implementat si o simulare a unei fabrici unde cuburile sunt produse. Aceste cuburi merg pe o banda rulanta si sunt detectate de o camera care le poate detecta culoarea, ceea ce rezulta la cresterea stocului in baza de date.

## Materiale si tehnologii folosite

Raspberry PI ZERO 2 W, conectat la modulul de camera si un senzor ultrasonic pentru detectarea distantei. Acesta este modulul ce se afla in 'fabrica' simulata. In momentul in care senzorul ultrasonic detecteaza un cub in vecinatatea sa, transmite imaginea camerei catre server care mai apoi este folosita pentru procesare.

Raspberry PI 5, folosit pentru a tine serverul in picioare. Aici ruleaza toate scripturile necesare API-ului si bazei de date care au fost scrise in Python (Flask). Este creierul intregii operatiuni. API-ul primeste de la modulul de camera imaginea cu cubul detectat, si folosind libraria OpenCV este detectata culoarea cubului din imagine. Apoi este procesata adaugarea sa in baza de date SQLLite.

Aplicatia WEB, scrisa folosind framewor-ul NEXT.js, este aplicatia E-commerce unde utilizatori pot vizualiza stocul de cuburi si de unde pot cumpara aceste produse. Aplicatia cere de la server intregul stoc de cuburi pentru a afisa utilizatorului stocul in timp real.
