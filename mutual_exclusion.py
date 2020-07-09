import threading, random, time

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Trabalho de SO: Matheus Santos Araujo, Gabriel Furtado Lins, Ivo Aguiar Pimenta
# Variáveis globais:

visitas = 0 # Variável global que representa a quantidade de visitas em um website internacional
qtd_servidores = 3 # Quantidade de servidores dos quais as visitas se originam (observe que esta variável também representa
				# a quantidade de threads, considerando que cada servidor atualiza independentemente sua contagem no site).
num_experimentos = 10 # Quantidade de experimentos iguais (para verificar quando ocorrem as condições de corrida, definido como 20 no experimento do artigo)
maximo_de_visitas = 10000 # Por servidor (Definido como 25.000 no experimento do artigo, quanto mais visitas mais condições de corrida)

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Criação de dados aleatórios:

def gerar_dados_reais(): 
	visitas_reais = [] # Cada índice do array representa a qtd real de visitas de cada servidor.
	for _ in range(qtd_servidores): visitas_reais.append(random.randint(0, maximo_de_visitas)) # Para cada servidor (índice do array),
																				 			   # adiciona um número aleatório de visitas
	return visitas_reais

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Funções para calcular as métricas:

def mean(v):
	_sum = 0.0
	for x in v: _sum += x
	return _sum/len(v)

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Sem exclusão mútua:

def incrementar_visitas(): # Função global (utilizada por todas as threads)
	global visitas
	visitas += 1

def adicionar_visitas(num_de_visitas):
	for _ in range(num_de_visitas):
		incrementar_visitas()

def rodar_contador():
	global visitas
	visitas = 0 # Reseta a qtd de visitas (caso queira fazer mais de 1 experimento)
	servidores = []
	visitas_reais = gerar_dados_reais()
	for i in range(qtd_servidores):
		servidores.append(threading.Thread(target=adicionar_visitas, args=(visitas_reais[i],)))
	for r in servidores: r.start() # Só começa a executar as threads aqui
	for r in servidores: r.join() # A main espera todas as threads terminarem a execução, para parar.
	total_de_visitas_reais = sum(visitas_reais)
	return total_de_visitas_reais

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Com exclusão mútua:

# ---------------------------------------------------------------------------------------------------------------------------
# Dekker:

def passar_turno(proximo_turno, turno, finish):
	if(all(finish)): return # Se todas as threads tiverem terminado, só retorna.
	if(proximo_turno == len(turno)): proximo_turno = 0 # Reseta o contador, se tiver chegado ao final do array de índices
	while(finish[proximo_turno]): # Enquanto não chegar em um que não tenha acabado...
		proximo_turno += 1 # Avança o índice do próximo turno
		if(proximo_turno == len(turno)): proximo_turno=0
	turno[proximo_turno] = True # Ativa o índice de turno da devida thread.

def algoritmo_dekker(quer_entrar, turno, thread_id, funcao_critica, finish):
	quer_entrar[thread_id] = True # Esta thread indica a intenção de entrar na região crítica
	while any(quer_entrar[:thread_id]+quer_entrar[thread_id+1:]): # Enquanto houver alguma thread que quer entrar:
		if(not turno[thread_id]): # Se não for o turno desta thread
			quer_entrar[thread_id] = False # Retira a intenção de entrar
			while (not turno[thread_id]): pass # Espera ocupada (espera a sua vez de entrar)
			quer_entrar[thread_id] = True
	# Após entrar na região crítica, faz o que tem que fazer:
	funcao_critica()
	# Agora passa a vez para a próxima thread:
	turno[thread_id] = False
	passar_turno(thread_id+1, turno, finish)
	quer_entrar[thread_id] = False

def adicionar_visitas_dekker(num_de_visitas, quer_entrar, turno, thread_id, finish):
	for _ in range(num_de_visitas):
		algoritmo_dekker(quer_entrar, turno, thread_id, incrementar_visitas, finish)
	finish[thread_id]=True  # Necessário para o caso de n>2 threads, uma vez que, caso o turno seja ativado para uma thread e esta já
							# tiver terminado, o programa ficará travado no turno da thread que finalizou.

def rodar_contador_dekker(): # Com dekker
	global visitas
	visitas = 0
	servidores = []
	visitas_reais = gerar_dados_reais()
	turno = [False]*qtd_servidores # Array indica de qual thread é a vez (o turno) de acessar a região crítica
	turno[0] = True # Faz com que a primeira thread inicie
	finish = [False]*qtd_servidores # Indica quais threads finalizaram (para lidar corretamente com o turno)
	quer_entrar = [False]*qtd_servidores
	for thread_id in range(qtd_servidores):
		servidores.append(threading.Thread(target=adicionar_visitas_dekker, args=(visitas_reais[thread_id], quer_entrar, turno, thread_id, finish)))
	for r in servidores: r.start()
	for r in servidores: r.join()
	total_de_visitas_reais = sum(visitas_reais)
	return total_de_visitas_reais

# ---------------------------------------------------------------------------------------------------------------------------
# Peterson:

def algoritmo_de_petterson(quer, ultimo, thread_id, funcao_critica):
	quer[thread_id] = True
	ultimo[0] = thread_id
	while(any(quer[:thread_id]+quer[thread_id+1:]) and ultimo[0]==thread_id): time.sleep(0.0001)
	# Região Crítica
	funcao_critica()
	# Saiu da região crítica
	quer[thread_id] = False

def adicionar_visitas_petterson(estagio, ultimo, thread_id, visitas_reais):
	for _ in range(visitas_reais):
		algoritmo_de_petterson(estagio, ultimo, thread_id, incrementar_visitas)

def rodar_contador_peterson():
	global visitas
	visitas = 0
	servidores = []
	visitas_reais = gerar_dados_reais()
	quer = [False]*qtd_servidores
	ultimo = [0]
	visitas_reais = gerar_dados_reais()
	for thread_id in range(qtd_servidores):
		servidores.append(threading.Thread(target=adicionar_visitas_petterson, args=(quer, ultimo, thread_id, visitas_reais[thread_id])))
	for r in servidores: r.start()
	for r in servidores: r.join()
	total_de_visitas_reais = sum(visitas_reais)
	return total_de_visitas_reais

# ---------------------------------------------------------------------------------------------------------------------------
# Lamport: 

def max(x):
	greater = 0
	for i in x: 
		if(i>greater): greater = i
	return greater

def comparing(tuple1, tuple2):
	if(tuple1[0] < tuple2[0]): return True
	elif(tuple1[0]==tuple2[0] and tuple1[1]<tuple2[1]): return True
	return False

def algoritmo_lamport(pegando, ticket, thread_id, funcao_critica):
	pegando[thread_id] = True
	ticket[thread_id] = max(ticket) + 1
	pegando[thread_id] = False
	for i in range(qtd_servidores):
		if(i==thread_id): continue
		while(pegando[i]): time.sleep(0.0001)
		while(ticket[i]!=0 and not comparing((ticket[thread_id], thread_id), (ticket[i],i))): time.sleep(0.0001)
	# Região crítica:
	funcao_critica()
	# Saiu da região crítica
	ticket[thread_id] = 0

def adicionar_visitas_lamport(pegando, ticket, thread_id, visitas_reais):
	for _ in range(visitas_reais):
		algoritmo_lamport(pegando, ticket, thread_id, incrementar_visitas)

def rodar_contador_lamport():
	global visitas
	visitas = 0
	servidores = []
	visitas_reais = gerar_dados_reais()
	pegando = [False]*qtd_servidores
	ticket = [0]*qtd_servidores
	for thread_id in range(qtd_servidores):
		servidores.append(threading.Thread(target=adicionar_visitas_lamport, args=(pegando, ticket, thread_id, visitas_reais[thread_id])))
	for r in servidores: r.start()
	for r in servidores: r.join()
	total_de_visitas_reais = sum(visitas_reais)
	return total_de_visitas_reais

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Implementação de experimentos:

def experimento(algorithm="Nenhum", num_experimentos=10):
	print("Legenda: (Visitas computadas / Número real de visitas) -> (Acerto ou Erro)")
	if(algorithm=="Nenhum"): contador = lambda : rodar_contador()
	elif(algorithm=="Dekker"): contador = lambda : rodar_contador_dekker()
	elif(algorithm=="Peterson"): contador = lambda : rodar_contador_peterson()
	elif(algorithm=="Lamport"): contador = lambda : rodar_contador_lamport()
	else: 
		print("Unknown algorithm!")
		return
	hits = 0.0
	times = []
	for i in range(num_experimentos):
		start = time.time()
		total_de_visitas_reais = contador()
		times.append(time.time()-start)
		print("({}/{}) -> {}".format(visitas, total_de_visitas_reais, "Acerto" if visitas==total_de_visitas_reais else "Erro"))
		if(visitas==total_de_visitas_reais): hits += 1.0
	total_time = mean(times)
	print("X ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X")
	print("Algoritmo de Exclusão Mútua: " + algorithm)
	print("Métricas:\n")
	print("Acertou {} de {} experimentos".format(int(hits), num_experimentos))
	acc = hits/float(num_experimentos)
	print("Acurácia total: {0:.2f} %".format(round(acc,4)*100))
	print("Tempo médio por experimento: {0:.4f} s".format(round(total_time, 4)))
	print("\nX ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X ~~~~~~~~~~~ X")

# ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~ X ~~~~~~~~~~~~~~~~~~
# Execução (Descomente o algoritmo em que deseja realizar o teste):

#experimento("Nenhum", 20)
#experimento("Dekker", 20)
#experimento("Peterson", 20)
#experimento("Lamport", 20)

