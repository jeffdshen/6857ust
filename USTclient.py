import hashlib
import random
import requests

SERVER_URL = "http://6857ust.csail.mit.edu"


# HASHING

def H(m):
    """
    return hash (256-bit integer) of string m, as long integer.
    If the input is an integer, treat it as a string.
    """
    m = str(m)
    return int(hashlib.sha256(m).hexdigest(),16)

def main():

    # This is the server's public key
    (n,e) = (134396116210830788484018767964013629489196469547696523589987670739352331298546935122669200918534934582132211415741993791432093579115340771967204360015313860402522803467667807760433738061050011496364124870297526881598059067254324554928263193228725822473875063136676943441129929543229462213961466613312291337393, 65537)

    # Replace this with the values you got from the course staff.
    # This is the nonce and sig(hash(nonce)) that would be received
    # through "subscription".
    (nonce, sig) = (15337433732377104068535799510106000550506956946754555476246382308813649548583,118687272508217959740691951638870343058827749400714658171161967268644009521942284681094396884289866427211323370699705391606713477379395010478259137908982763217640693520207051359681150367480936274815349949745757165617955533701361528393874168833356690522601843456559898721121862441279029199777138508369493409505)

    # Number of iterations.  Please don't make this very large.
    num_iterations = 1

    for i in xrange(0,num_iterations):
        #generate a new nonce (new_nonce) and blinded object (blinded_new_hash) to sign
        new_nonce = random.getrandbits(256)
        r = random.getrandbits(256)
        blinded_new_hash = blind(n, e, r, H(new_nonce))

        #make a request to the server
        print "new_nonce:", new_nonce
        print "r:", r
        (text_string, new_blinded_sig) = send_request(sig, nonce, blinded_new_hash)
        new_blinded_sig = long(new_blinded_sig)

        # If you feel like printing out any other information, here's
        # a good place to do it...
        print text_string
        print new_blinded_sig

        #unblind the new sig (yielding new_sig)
        new_sig = unblind(n, r, new_blinded_sig)

        print "unblinded:", new_sig

        #change to next nonce/signature for next iteration
        (nonce, sig) = (new_nonce, new_sig)

def blind(n, e, r, x):
    y = x % n
    for i in xrange(e):
        y = (y * r) % n
    return y

def unblind(n, r, y):
    return (y * modinv(r, n)) % n

# iterative egcd and modinv from Wikibooks
# License https://creativecommons.org/licenses/by-sa/3.0/
def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    gcd = b
    return gcd, x, y

def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

# Send a request of the form sig(hash(nonce)), nonce, blind(hash(new_nonce))
def send_request(signed_hash, nonce, blinded_new_hash):
    payload = {'sig': signed_hash, 'nonce': nonce, 'blinded': blinded_new_hash}
    r = requests.get(SERVER_URL, params=payload)
    if(r.status_code != 200):
        raise Exception(r.text)
    return r.text.splitlines()

main()
