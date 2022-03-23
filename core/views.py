from django.shortcuts import *
from django.contrib.auth import  authenticate, login as d_login, logout as d_logout
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
import hashlib
import bitcoin
from bitcoin import *
import random
from django.db.models import Q




def index(request):
    if request.user.is_authenticated:
        user = request.user
        profile = Profile.objects.get(user = user)        
        wallet = Wallet.objects.filter(user = profile)
        if wallet.exists():
            wallet_id = wallet.first().id
            transactions = Transaction.objects.filter(receiver = wallet_id, status = "PENDING")
            if transactions.exists():
                numbers = transactions.count()
                context = {
                    "numbers":numbers,
                    "transactions":transactions,
                    "wallet_id":wallet_id,
                }
            else:
                numbers = 0
                context = {"numbers":numbers}
        else:
            context = {}
    else:
        context = {}
    return render(request, "core/home.htm", context)


def register(request):
    return render(request, 'core/signup.htm', {})


def register_save(request):
    if request.method == "POST":
        username = request.POST.get('username') 
        email = request.POST.get('email')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')

        if password==password1:       
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email Taken')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username Taken')
                return redirect('register')
            elif User.objects.filter(username = username).exists() and User.objects.filter(email=email).exists():
                messages.error(request, "Username and Email Taken")
                return redirect('register')

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            print('User Created')
            return redirect('login')

        messages.error(request, 'Passwords Do Not Match')
        return redirect('register')
    return HttpResponse("<h2> This request is Invalid </h2> ")



def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)
        if user != None:
            auth.login(request, user)
            return redirect('index')

        messages.error(request, "Invalid Credentials")
        return redirect('login')

    return render(request, 'core/login.htm', {})



def logout(request):
    d_logout(request)
    return redirect('index')


def wallet(request):
    user = request.user
    profile = Profile.objects.get(user = user)

    try:
        wallet = Wallet.objects.get(user = profile)
        transactions = Transaction.objects.filter(receiver = wallet, status = "PENDING")
        numbers = transactions.count()
        context = {
            "numbers":numbers,
            "transactions":transactions,
            "wallet":wallet,
        }
    except:
        context = {}
    return render(request, "core/wallet.html", context)



def generate_address(request):
    user = request.user
    profile = Profile.objects.get(user = user)
    private_key = bitcoin.random_key()
    public_key = bitcoin.privtopub(private_key)
    address = bitcoin.pubtoaddr(public_key)
    wallet = Wallet(user = profile, wallet_addr = address, wallet_bal = 0)
    wallet.save()
    return redirect("wallet")



def send_coin(request):
    return render(request, 'core/send_coin.htm', {})


def send_coin_save(request):
    if request.method == "POST":
        address = request.POST.get('address')
        amount = request.POST.get('amount')
        amount_int = int(amount)
        user = request.user
        profile = Profile.objects.get(user = user)
        wallet = Wallet.objects.get(user = profile)

        if amount_int > int(wallet.wallet_bal):
            messages.error(request, " Insuffecient Coins In Wallet! ")
            return redirect(request.META.get("HTTP_REFERER"))

        elif address == str(wallet):
            messages.error(request, " Sorry You Cannot Send Coin To Yourself! ")
            return redirect(request.META.get("HTTP_REFERER"))

        try:
            wallet_receiver = Wallet.objects.filter(wallet_addr = address)
            wallet_receiver_first = wallet_receiver.first()
            if wallet_receiver_first is None:
                messages.error(request, " Invalid Address! ")
                return redirect(request.META.get("HTTP_REFERER"))

            print(amount_int)
            print(wallet_receiver)

            h = hashlib.sha256()
            a = random.randint(1, 18364983649347348345)
            h.update(str(a).encode('utf-8'))
            cipher_key = h.hexdigest()
            wallet_receiver_handle = wallet_receiver_first.user.user.username
            wallet_receiver_handle_int = str(random.randint(1, 73827832323)) + str(wallet_receiver_handle[:3])
            hw = hashlib.sha256()
            hw.update(str(wallet_receiver_handle_int).encode('utf-8'))
            transaction_id = hw.hexdigest()

            print(wallet_receiver_handle[:3])
            print(wallet_receiver_handle_int)
            print(transaction_id)

            transaction = Transaction(transaction_id=transaction_id, transaction_cipher_key=cipher_key, sender = wallet, receiver = wallet_receiver_first, transaction_amount = amount_int, status = "PENDING")
            transaction.save()

            remaining = wallet.wallet_bal - amount_int
            wallet.wallet_bal = remaining
            wallet.save()

            messages.success(request, "Sent " + str(amount) + " Bitcoins Successfully! ")
            messages.success(request, "Your Cipher Shared Key Is :")
            messages.success(request, str(cipher_key))
            return redirect(request.META.get("HTTP_REFERER"))
        
        except:
            messages.error(request, " Transaction Failed ")
            return redirect(request.META.get("HTTP_REFERER"))
       

    
def receive_coin(request):
    return render(request, 'core/receive_coin.htm', {})


def receive_coin_save(request):
    if request.method == "POST":
        cipher_key = request.POST.get('cipher_key')
        user = request.user
        profile = Profile.objects.get(user = user)

        transaction = Transaction.objects.filter(transaction_cipher_key=cipher_key)
        transaction_ = transaction.first()
        wallet = Wallet.objects.get(user = profile)


        if transaction.first() is None:
            messages.error(request, "Invalid Cipher Key")
            return redirect(request.META.get("HTTP_REFERER"))

        elif transaction.first().status == "RECEIVED":
            messages.error(request, "Please use a Valid Cipher Key")
            return redirect(request.META.get("HTTP_REFERER"))

        elif transaction_.receiver.wallet_addr != wallet.wallet_addr:
            messages.error(request, "Ooops!!, This Coin Is Not Meant For You!")
            return redirect(request.META.get("HTTP_REFERER"))

        wallet.wallet_bal = wallet.wallet_bal + transaction.first().transaction_amount
        wallet.save()

        receive_transac = Receive_transaction(transaction_obj = transaction.first())
        receive_transac.save()

        transaction_.status = "RECEIVED"
        transaction_.save()
        messages.success(request, "Received " + str(transaction_.transaction_amount) + " Bitcoins Successfully")
        return redirect(request.META.get("HTTP_REFERER"))

    

def history(request):
    user = request.user
    profile = Profile.objects.get(user = user)
    wallet = Wallet.objects.get(user = profile)
    transactions = Transaction.objects.filter(Q(receiver = wallet) | Q(sender = wallet))

    if transactions is None:
        context = {

        }
    else:
        transaction = transactions.count()
        context = {
            "transactions":transactions,
            "transaction":transaction
        }
    return render(request, "core/history.htm", context)