## Projekt 1 - dokumentacja
Zadaniem projektowym było napisanie skryptu umożliwiającego przenoszenie przedmiotów przez robota Velma
pomiędzy znajdującym się w jej zasięgu punktami.

### Uruchomienie 
1. Na początku należy pobrać i zbudować pakiet (komenda `catkin build`)
2. W każdym nowo otwartym oknie terminala należy wykonać: `source $HOME/mobile_ws/devel/setup.bash` - zakładając
że `mobile_ws` to nazwa folderu z przestrzenią roboczą w której znajduję się pobrany pakiet 
3. Następnie w kolejnych oknach terminala:
* `roslaunch manipulation velma_system_online.launch`
* `roslaunch velma_ros_plugin velma_planner.launch`
* `rosrun rcprg_ros_utils run_rviz.sh`
* Dodatkowo można uruchomić symulator Gazebo: `roslaunch rcprg_gazebo_utils gazebo_client.launch`
Przydatnym poleceniem może być również: `rosrun velma_common reset_shm_comm.py` resetujące system sterowania robotem Velma

4. Program uruchamiany jest za pośrednictewm skryptu `moj_wspanialy_wezel.py`:
* `python moj_wspanialy_wezel.py` - polecenie nalezy wykonac w katalaogu z danym skryptem
* `python moj_wspanialy_wezel.py online` - opcja z octomapą generowaną na bieżąco 

### Działanie programu
W przypadku opcji octomapy generowanej online, na początku programu uruchamiane jest zachowanie skanowania:

![skanowanie](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/octomap1.png)

Przed jego rozpoczęciem zamykane są palce w dłoni robota - tak aby uniknąć potencjalnych kolizji.

Następnie zczytywane jest położenie słoika. Na jego podstawie planowana jest trajektoria ruchu do tego przedmiotu.
Ruch wykonywany jest w przestrzeni stawów (jint_imp). Po zbliżeniu się do słoika tryb ruchu zamieniany jest na kartezjańsk - 
w przestrzeni końcówki (cart_imp), którym to dłoń porusza się bezpośrednio do słoika. 

![zblizenie](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/lapie1.png)

Po złapaniu słoika, podnoszony jest on nadal kartezjańskim trybem ruchu, po czym zamieniany jest on na ruch w przestrzeni złącz.

![niesie](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/trzyma3.png)

Następnie przenoszony jest on na drugi stół i odstawiany.
![niesie](https://github.com/STERO-21Z/groszyk-zembron/blob/tiago/manipulation/docs/odstawia.png)
