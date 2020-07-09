# Exclusao-mutua-aplicada-em-acessos-de-um-servidor-web
O controle de um sistema web é um desafio que vem crescendo visto que as arquiteturas modernas estão cada vez mais distribuı́das, logo são necessárias técnicas para manter consistentes as informações dos sistemas e evitar que dados de servidores diferentes de uma mesma aplicação acabe tendo dados conflitantes ou desatualizados. A partir dessa problemática, desenvolve- mos uma solução de exclusão mútua em um servidor web distribuı́do o qual contém diversas máquinas atualizando a variável de controle de acessos em um website cliente e consequentemente gerando conflitos, os quais são resolvidos utilizando os algoritmos de Peterson, Dekker e Lamport.
