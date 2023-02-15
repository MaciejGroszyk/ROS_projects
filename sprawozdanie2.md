## Projekt 2 - dokumentacja
W ramach drugiego projektu należano napisać program, który sprawi, że robot Velma otworzy drzwi szafki (jedne, o co najmniej 90 stopni), a następnie robot wróci do pozycji początkowej.


### Uruchomienie 
1. Na początku należy pobrać i zbudować pakiet (komenda `catkin build`)
2. W każdym nowo otwartym oknie terminala należy wykonać: `source $HOME/mobile_ws/devel/setup.bash` - zakładając
że `mobile_ws` to nazwa folderu z przestrzenią roboczą w której znajduję się pobrany pakiet 
3. Następnie w kolejnych oknach terminala:
* `roslaunch manipulation p2_velma_system_online.launch`
* `roslaunch velma_ros_plugin velma_planner.launch`
* `rosrun rcprg_ros_utils run_rviz.sh`
* Dodatkowo można uruchomić symulator Gazebo: `roslaunch rcprg_gazebo_utils gazebo_client.launch`
Przydatnym poleceniem może być również: `rosrun velma_common reset_shm_comm.py` resetujące system sterowania robotem Velma

4. Program uruchamiany jest za pośrednictewm skryptu `moj_wspanialy_wezel.py`:
* `p2_python moj_wspanialy_wezel.py` - polecenie nalezy wykonac w katalaogu z danym skryptem
* `p2_python moj_wspanialy_wezel.py online` - opcja z octomapą generowaną na bieżąco 

### Działanie programu
W przypadku opcji octomapy generowanej online, na początku programu uruchamiane jest zachowanie skanowania świata:


![velma_skanuj](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/velma_octo.png)

Po otrzymaniu obrazu świata można rozpocząć planowanie ruchu - robot zbliża swoje ramię w okolicę klamki (poruszając się w trybie joint impedance - w przestrzeni złączy), następnie tryb ruchu jest zamieniany na cartesian impedance i rozpoczyna się próba chwycenia za klamkę:


![blisko_klamki](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/velma_blisko_klamki.png)


Gdy robot wykonuje ruch bezpośrednio w stronę klamki zmniejszana jest jego impedancja - aby nie doszło do wyłamania klamki. Następnie robot (trzymając klamkę) stara się osiągnąć kilka punktów które zostały wyznaczone na łuku zakreślanym przez drzwiczki.


![klamka_zlapana](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/velm_p2_1.png)

 Po wychyleniu ich do kąta prostego klamka jest puszczana a robot powraca do pozycji początkowej.

![drzwi_wychylone_90](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/velma_p2_2.png)


## Diagram aktywności
Jest to koncepcyjny diagram aktywnośći, obrazujący bardzo ogólnie i prostym językiem działanie systemu. Odwołuje się on wprost do diagramu sekwencji, na którym to przedstawiono program bardziej szczegółowo.

![diagram_aktywnosci](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/Koncepcyjny%20Diagram%20Aktywno%C5%9Bci.jpg)

## Diagram wymagań
Na diagramie przedstawiono główne zadania wraz z podzadaniami.


![wymagania_funkcyjne](https://user-images.githubusercontent.com/80107636/150539065-496d6ccc-9846-448b-b251-1170c3074497.jpg)

## Diagram definiowania bloków
Przedstawia on elementy które wchodzą w skład świata w którym działa robot Velma.

![bdd](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/bddvelma.jpg)

## Diagram przypadków użycia
Na diagramie przedstawiono w jaki sposób użytkownik może korzystać z systemu. Możliwą ingerencją człowieka jest odpalenie programu z odpowiednim parametrem oraz ewentualne awaryjne przerwanie programu.

![diagram_przypadkow_uzycia](https://user-images.githubusercontent.com/80107636/150539218-ad522307-adf7-4f66-8e04-562b4fee6779.jpg)

## Diagram sekwencji
Diagram sekwencji został zdekomponowany na 4 części (inicjalizacja, ruch w pobliże szafki, otwieranie szafki, powrot do pozycji początkowej), każdej z nich odpowiada akcja wykonywana przez węzeł. Poddiagramy zawierają w sobie również przesyłane parametry między ostatnimi klasami wywołującymi konkretne zadania (kropka przy strzałce zinterpetowano jako sposób ukazania połączenia pomiędzy blokami w poddiagramie). Parametry te głównie polegają na przekazaniu informacji o prawidłowym wykonaniu zadania. W implementacji zadania uwzględniono także sytuacje niepowodzenia i komunikacji błędu. Nie zostały one przedstawione na diagramach w celu nie zaciemniania głównej funkcji programu.
Jako bloki w diagramie sekwencji, zostały zdefiniowane w sposób opisowy klasy (bloki opisują działanie danej klasy, nie jej dokładną nazwę). 

![diagram_sekwencji](https://user-images.githubusercontent.com/80107636/150537956-12de9529-ece3-4a74-82d5-7977ffca2f8a.jpg)

Poddiagram inicjalizacji wykorzystuje klasy do inicjalizacji oraz skanowania octomapy lub wczytwania wersji offline octomapy.

![INICJALIZACJA](https://user-images.githubusercontent.com/80107636/150537988-7071cc11-541e-4842-bb97-a4266576e45d.jpg)

Poddiagram ruch w pobliże szafki. Wykorzystano w nim klasy, których zadaniem jest ruch do pozycji początkowej, obliczenie odwrotnej kinematyki oraz osiągniecie pozycji blisko szafki. Zadania te umieszczone są w pętli. Warunkiem wyjścia z pętli jest powodzenie osiągnięcia pozycji blisko szafki.

![RUCH W POBLIŻE SZAFKI](https://user-images.githubusercontent.com/80107636/150537919-7b90da1d-32b0-4140-9c5e-80a008ebdad0.jpg)

Poddiagram otwieranie szafki. Wykorzystano w nim klasy, których zadaniem jest złapanie klamki oraz otworzenie drzwi szafki. Otwieranie drzwi w szafce zostało podzielone na fragmenty (drzwi nie są otwierane w jednym podejściu, robot pare razy uchyla drzwi coraz szerzej)

![OTWIERANIE SZAFKI](https://user-images.githubusercontent.com/80107636/150537997-b18ec5df-bb87-439f-b266-c2bc576157cd.jpg)

Poddiagram powrót do pozycji początkowej wykorzystuje jedną klasę, której zadaniem jest osiągnięcie pozycji startowej robota.

![POWRÓT DO POZYCJI POCZĄTKOWEJ](https://user-images.githubusercontent.com/80107636/150538009-b7fac680-5f9e-4275-9292-d4ea257a26a0.jpg)

