import requests, random, re, json, sys, pymysql
from bs4 import BeautifulSoup
from time import sleep

#site email
siteEmail = "https://10minutemail.net"
#proxies
proxies={"http":"http://80.94.122.222:8080"}


#=======================gerar senha
def criarSenha():
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    senha=""
    for x in range(8):
        senha+=random.choice(caracteres)
    if(senha != ""):
        print("Senha: ", senha)
        return senha
    else:
        print("Erro ao gerar senha.")
   

#=======================logar no instagram
def logar(email, senha):
    data3={'username': email, 'password': senha}
    req_logar=requests.Session()
    req_cookies= req_logar.get("https://www.instagram.com/accounts/login/")
    cookies = dict(req_cookies.cookies)
    req_logar.headers.update({"X-CSRFToken":cookies['csrftoken']})
    result = req_logar.post("https://www.instagram.com/accounts/login/ajax/", data=data3, allow_redirects=True)
    if(result.status_code == 200):
        print("Logado.")
        return dict(result.cookies)
    else:
        print("Erro ao logar.")


#=======================dados da nova conta
def dadosConta():
    data={"country": "BR"}
    req_pessoa = requests.post("https://www.invertexto.com/gerador-de-pessoas", data=data)
    bsObj = BeautifulSoup(req_pessoa.content,'html.parser')
    pessoa_dados = bsObj.findAll("input",{"class":"form-control"});
    if(pessoa_dados[0].get("value") != ""):
        print("Dados pessoa criado.")
        return pessoa_dados[0].get("value")
    else:
        print("Erro ao criar os dados.")   


#=======================dados email
def criarEmail():
    req_email = requests.get(siteEmail)
    bsObj = BeautifulSoup(req_email.content,'html.parser')
    email = bsObj.findAll("input",class_="mailtext")[0].get("value")
    if(email != ""):
        print("Email criado: ",email)
        return [email,dict(req_email.cookies)]
    else:
        print("Erro ao criar email.")
    

#=======================pegar id da pessoa instagram
def pegarId(pessoa_seguida):
    pegarid = requests.get(pessoa_seguida)
    bsObj = BeautifulSoup(pegarid.content, 'html.parser')
    js = re.compile("window._sharedData")
    sharedata = bsObj.find("script", text=js)
    sharedata = sharedata.get_text()
    #o [:-1] elimina o ultimo caractere da string
    sharedata = sharedata.replace("window._sharedData = ","")[:-1]
    #tirando esses caracteres pois da erro com a norma utf-8
    sharedata = sharedata.replace("\\u", "")
    data = json.loads(sharedata)
    ident= data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
    if(pegarid.status_code == 200 and ident != ""):
        print("Identificador pego.")
        return [ident,pessoa_seguida]

    else:
        print("Erro ao pegar o identificador.")
    

#=======================seguir pesssoa
def seguir(cookies, id_pessoaSeguida, seguir, pessoa_seguida):
    req_seguir = requests.Session()
    req_seguir.headers.update({
                         "origin":"https://www.instagram.com",
                         "referer":pessoa_seguida,
                         "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.71",
                         "X-CSRFToken":cookies['csrftoken'],
                         "x-requested-with":"XMLHttpRequest"})
    if(seguir == 1):
        result = req_seguir.post("https://www.instagram.com/web/friendships/"+id_pessoaSeguida+"/follow/", cookies=cookies, allow_redirects=True)
        if(result.status_code != 200):
            print("Erro ao seguir.")
        else:            
            print("Seguindo.")
    elif(seguir == 2):
        result = req_seguir.post("https://www.instagram.com/web/friendships/"+id_pessoaSeguida+"/unfollow/", cookies=cookies, allow_redirects=True)
        if(result.status_code != 200):
            print("Erro ao seguir.")
        else:            
            print("Deixando de seguir.")
    else:
        print("Erro. No terceiro parametro digite 1-Seguir, 2-deixar de seguir.")
    
        
#=======================criar conta instagram
def criarInsta(proxies, dados_pessoa, email, senha):
    #pegando sugestao de nome
    abrirInsta = requests.get("https://www.instagram.com/", proxies = proxies)
    cookies = dict(abrirInsta.cookies)
    nome ={"first_name":dados_pessoa}
    headerCookies={"origin": "https://www.instagram.com",
                   "referer": "https://www.instagram.com/",
                   "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                   "x-csrftoken":cookies["csrftoken"],
                   "x-requested-with": "XMLHttpRequest"}
    atualizar = requests.post("https://www.instagram.com/accounts/web_create_ajax/attempt/", proxies = proxies, headers=headerCookies, data=nome, allow_redirects=True)
    pegarNomeUsuario = json.loads(atualizar.text)
    #criando a conta
    dadosConta = {"email":email,
                "password":senha,
                "username":pegarNomeUsuario["username_suggestions"][0],
                "first_name": dados_pessoa}
    criarConta = requests.post("https://www.instagram.com/accounts/web_create_ajax/", proxies = proxies, headers=headerCookies, data=dadosConta)
    if(criarConta.status_code == 200):
        print("Conta criada. \n Email: ",email,"\n Senha: ",senha,"\n Nome: ",pegarNomeUsuario["username_suggestions"][0])
    else:
        print("Erro ao criar conta.")

 
#=======================verificar e ativar email
def EmailConf(siteEmail, cookies, proxies):
    emailConfirmacao = []
    count = 0
    while(len(emailConfirmacao) < 4):
        entrarEmail2 = requests.get(siteEmail, cookies=cookies)
        bsObj = BeautifulSoup(entrarEmail2.content,"html.parser")
        emailConfirmacao = bsObj.find("table",id="maillist").select("td")
        if(count>6):
            print("Tempo de espera esgotado.")
            return 0
            break
        if((str(emailConfirmacao[0]).find("Instagram"))>0):
            linkConf = bsObj.find("table",id="maillist").select("td a")
            if(len(linkConf) >= 2):
                link = linkConf[0].get("href")
                confLink = requests.get(siteEmail+"/"+link, cookies=cookies)
                bsObj = BeautifulSoup(confLink.content,"html.parser")
                listaLinks = bsObj.findAll("a")
                for i in listaLinks:
                    if(str(i).find("https://instagram.com/accounts/confirm_email")>0):
                        result = requests.get(i.get("href"), proxies = proxies)
                        print(result.status_code)
                        print("Confirmação concluida.")
                        return 1
                       # break
            else:
                print("Erro. não possui link para confirmação.")
                return 0
        else:
            print("Esperando email.")
        sleep(100)
        count+=1

#===============================================
#=======================MAIN====================



def conta_criar_seguir():
    emailAtv = criarEmail()
    novasenha=criarSenha()
    criarInsta(proxies, dadosConta(), emailAtv[0], novasenha)
    confirmado = EmailConf(siteEmail,emailAtv[1], proxies)
    if(confirmado == 1):
        sleep(250)
        cookies = logar(emailAtv[0],novasenha)
        ident=pegarId("https://www.instagram.com/pessoa.xxxxx/")
        seguir(cookies,ident[0],1,ident[1])


def conta_seguir(email,senha):
    cookies = logar(email,senha)
    ident=pegarId("https://www.instagram.com/pesso.xxxxxxx/")
    seguir(cookies,ident[0],1,ident[1])

#seguir alguem
#conta_seguir("meuinsta.com","senha")

conta_criar()
    








