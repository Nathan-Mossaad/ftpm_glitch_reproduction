# On teensy
# set glitch ping_wait 600000
# tail -f `ls -r attack*.txt | head -n1`
# 
python -u attack.py > "attack-$(date -Is).txt"
