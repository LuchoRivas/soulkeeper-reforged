PERM=[16,2,6,8,19,17,11,12,1,3,0,9,18,7,5,10,13,4,14,15]
def decode(s):
    L=len(s)
    if L==0: return ''
    cols=L//5; cols=20 if cols>20 else (1 if cols==0 else cols)
    rem=L%cols; rows=(L-rem)//cols
    arr={}; i=0; j=0
    while i<L:
        if j<rem:
            i+=1; arr[PERM[j]+(rows+1)*20]=s[i-1]
        for k in range(1,rows+1):
            i+=1; arr[PERM[j]+(rows-k+1)*20]=s[i-1]
        j+=1
    out=''; c=0; r=1
    for _ in range(L):
        if c>=cols: r+=1; c-=cols
        out+=arr.get(PERM[c]+r*20,''); c+=1
    return out
def encode(plain):
    # decode is a fixed permutation of positions for a given length: invert it
    L=len(plain); probe=[chr(0x100+i) for i in range(L)]
    d=decode(''.join(probe)); assert len(d)==L
    res=['']*L
    for outpos,ch in enumerate(d): res[ord(ch)-0x100]=plain[outpos]
    e=''.join(res); assert decode(e)==plain; return e
