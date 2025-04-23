from choosePreference import*

s='L'
lowerseatcount=2
middleseatcount=2
upperseatcount=2
sidelowerseatcount=2
sideupperseatcount=2

racseatcount=2
waitingseatcount=2

L=[lowerseatcount,middleseatcount,upperseatcount,sidelowerseatcount,sideupperseatcount,racseatcount]

loop=True

while(s!='q'):
    s=input("Enter Preference : ")
    print(preference(s,L))

    