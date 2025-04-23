def preference(pref,L):

    # L=[lowerseatcount,middleseatcount,upperseatcount,sidelowerseatcount,sideupperseatcount,racseatcount]

    if pref=='L':
        lst = [0, 1, 2, 3, 4]
    elif pref=='M':
        lst = [1, 0, 2, 3, 4]
    elif pref=='U':
        lst = [2, 0, 1, 3, 4]
    elif pref=='SL':
        lst = [3, 0, 1, 2, 4]
    elif pref=='SU':
        lst = [4, 0, 1, 2, 3]
    else:
        return '\0'
    

    for i in lst:
        if (L[i]>0):
            L[i]-=1
            return ['L', 'M', 'U', 'SL', 'SU'][i]
    if L[5]>0:
        L[5]-=1
        return 'rac'

    return 'waiting'


    '''

    if (L[2]==0 and L[1]==0 and L[0]==0):
        if(L[3]!=0):
            L[3]-=1
            return 'rac'
        else:
            return 'waiting'
    
    if(pref=='L'):
        if(L[0]>0):
            L[0]-=1
            return 'L'
        if(L[2]>0):
            L[2]-=1
            return 'U'
        else:
            L[1]-=1
            return 'M'
    
    if(pref=='M'):
        if(L[1]>0):
            L[1]-=1
            return 'M'
        if(L[2]>0):
            L[2]-=1
            return 'U'
        else:
            L[0]-=1
            return 'L'
        
    if(pref=='U'):
        if(L[2]>0):
            L[2]-=1
            return 'U'
        if(L[0]>0):
            L[0]-=1
            return 'L'
        else:
            L[1]-=1
            return 'M'

    return'\0'

    '''