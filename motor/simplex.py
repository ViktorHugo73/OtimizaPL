"""
motor_simplex.py
Motor isolado de Programação Linear para o TCC.

Características da versão 0.1:
- minimização e maximização;
- restrições <=, >= e =;
- variáveis de decisão não negativas;
- Simplex em duas fases;
- detecção de solução ótima, inviabilidade e ilimitado;
- regra de Bland para reduzir risco de ciclagem;
- sem dependência de interface, API ou banco de dados.

Dependência:
    pip install numpy
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class ResultadoPL:
    status: str
    x: Optional[np.ndarray]
    valor_objetivo: Optional[float]
    iteracoes_fase1: int
    iteracoes_fase2: int
    mensagem: str


class SimplexDuasFases:
    """
    Resolve:
        max/min c^T x

    sujeito a:
        A_i x (<=, >=, =) b_i
        x >= 0

    Observação:
    limites superiores podem ser modelados como restrições, por exemplo:
        x1 <= 8
    """

    def __init__(self, tolerancia: float = 1e-9, max_iteracoes: int = 10000):
        self.tol = tolerancia
        self.max_iteracoes = max_iteracoes

    def resolver(
        self,
        A: List[List[float]],
        b: List[float],
        c: List[float],
        operadores: List[str],
        objetivo: str = "max",
    ) -> ResultadoPL:

        A = np.asarray(A, dtype=float)
        b = np.asarray(b, dtype=float)
        c = np.asarray(c, dtype=float)

        self._validar_entrada(A, b, c, operadores, objetivo)

        A_padrao, b_padrao, base, artificiais, n_originais = \
            self._construir_forma_padrao(A, b, operadores)

        # ---------------- FASE I ----------------
        iter_fase1 = 0

        if artificiais:
            c_fase1 = np.zeros(A_padrao.shape[1], dtype=float)

            # Maximizar - soma(variáveis artificiais)
            for j in artificiais:
                c_fase1[j] = -1.0

            status, x1, z1, base, iter_fase1 = self._simplex_primal(
                A_padrao, b_padrao, c_fase1, base
            )

            if status != "optimal":
                return ResultadoPL(
                    status=status,
                    x=None,
                    valor_objetivo=None,
                    iteracoes_fase1=iter_fase1,
                    iteracoes_fase2=0,
                    mensagem="Falha durante a Fase I do Simplex.",
                )

            # z1 = - soma(artificiais). Para ser factível, z1 deve ser 0.
            if z1 < -1e-7:
                return ResultadoPL(
                    status="infeasible",
                    x=None,
                    valor_objetivo=None,
                    iteracoes_fase1=iter_fase1,
                    iteracoes_fase2=0,
                    mensagem="O modelo não possui solução factível.",
                )

            A_fase2, b_fase2, base_fase2, colunas_mantidas = \
                self._remover_artificiais(
                    A_padrao, b_padrao, base, artificiais
                )
        else:
            A_fase2 = A_padrao
            b_fase2 = b_padrao
            base_fase2 = base
            colunas_mantidas = list(range(A_padrao.shape[1]))

        # ---------------- FASE II ----------------

        # O núcleo trabalha sempre como maximização.
        if objetivo.lower() == "max":
            c_max = c.copy()
        else:
            c_max = -c.copy()

        c_fase2 = np.zeros(A_fase2.shape[1], dtype=float)

        for indice_original in range(n_originais):
            indice_novo = colunas_mantidas.index(indice_original)
            c_fase2[indice_novo] = c_max[indice_original]

        status, x2, _, _, iter_fase2 = self._simplex_primal(
            A_fase2, b_fase2, c_fase2, base_fase2
        )

        if status == "unbounded":
            return ResultadoPL(
                status="unbounded",
                x=None,
                valor_objetivo=None,
                iteracoes_fase1=iter_fase1,
                iteracoes_fase2=iter_fase2,
                mensagem="A função objetivo é ilimitada na região factível.",
            )

        if status != "optimal":
            return ResultadoPL(
                status=status,
                x=None,
                valor_objetivo=None,
                iteracoes_fase1=iter_fase1,
                iteracoes_fase2=iter_fase2,
                mensagem="O algoritmo não concluiu com solução ótima.",
            )

        x_original = np.array(
            [
                x2[colunas_mantidas.index(j)]
                for j in range(n_originais)
            ],
            dtype=float,
        )

        x_original[np.abs(x_original) < self.tol] = 0.0
        z_original = float(c @ x_original)

        return ResultadoPL(
            status="optimal",
            x=x_original,
            valor_objetivo=z_original,
            iteracoes_fase1=iter_fase1,
            iteracoes_fase2=iter_fase2,
            mensagem="Solução ótima encontrada.",
        )

    # ------------------------------------------------------------------

    def _validar_entrada(self, A, b, c, operadores, objetivo):
        if A.ndim != 2:
            raise ValueError("A deve ser uma matriz bidimensional.")

        m, n = A.shape

        if m == 0 or n == 0:
            raise ValueError("O modelo deve possuir variáveis e restrições.")

        if b.shape != (m,):
            raise ValueError("O tamanho de b deve ser igual ao número de restrições.")

        if c.shape != (n,):
            raise ValueError("O tamanho de c deve ser igual ao número de variáveis.")

        if len(operadores) != m:
            raise ValueError("Deve existir um operador para cada restrição.")

        if any(op not in ("<=", ">=", "=") for op in operadores):
            raise ValueError("Operadores válidos: <=, >= e =.")

        if objetivo.lower() not in ("max", "min"):
            raise ValueError("objetivo deve ser 'max' ou 'min'.")

        if not np.isfinite(A).all() or not np.isfinite(b).all() or not np.isfinite(c).all():
            raise ValueError("A, b e c devem conter apenas valores numéricos finitos.")

    # ------------------------------------------------------------------

    def _construir_forma_padrao(self, A, b, operadores):
        A = A.copy()
        b = b.copy()
        operadores = list(operadores)

        m, n = A.shape

        # Normaliza RHS negativo.
        for i in range(m):
            if b[i] < 0:
                A[i, :] *= -1
                b[i] *= -1

                if operadores[i] == "<=":
                    operadores[i] = ">="
                elif operadores[i] == ">=":
                    operadores[i] = "<="

        linhas = [list(A[i, :]) for i in range(m)]
        base = [-1] * m
        artificiais = []
        numero_colunas = n

        def adicionar_coluna(valores):
            nonlocal numero_colunas

            for i, valor in enumerate(valores):
                linhas[i].append(float(valor))

            indice = numero_colunas
            numero_colunas += 1
            return indice

        for i, op in enumerate(operadores):
            if op == "<=":
                coluna = [0.0] * m
                coluna[i] = 1.0
                base[i] = adicionar_coluna(coluna)

            elif op == ">=":
                # Variável de excesso.
                coluna = [0.0] * m
                coluna[i] = -1.0
                adicionar_coluna(coluna)

                # Variável artificial.
                coluna = [0.0] * m
                coluna[i] = 1.0
                indice_artificial = adicionar_coluna(coluna)

                base[i] = indice_artificial
                artificiais.append(indice_artificial)

            else:  # =
                coluna = [0.0] * m
                coluna[i] = 1.0
                indice_artificial = adicionar_coluna(coluna)

                base[i] = indice_artificial
                artificiais.append(indice_artificial)

        return (
            np.asarray(linhas, dtype=float),
            b,
            base,
            artificiais,
            n,
        )

    # ------------------------------------------------------------------

    def _simplex_primal(self, A, b, c, base):
        """
        Núcleo Simplex para maximização com uma base factível conhecida.
        Utiliza custos reduzidos e regra de Bland.
        """

        A = np.asarray(A, dtype=float)
        b = np.asarray(b, dtype=float)
        c = np.asarray(c, dtype=float)
        base = list(base)

        m, n = A.shape

        for iteracao in range(1, self.max_iteracoes + 1):
            B = A[:, base]

            try:
                xB = np.linalg.solve(B, b)
                B_inv_A = np.linalg.solve(B, A)
            except np.linalg.LinAlgError:
                return "numerical_error", None, None, base, iteracao

            xB[np.abs(xB) < self.tol] = 0.0

            if np.min(xB) < -1e-7:
                return "numerical_error", None, None, base, iteracao

            cB = c[base]

            # r_j = c_j - c_B^T B^-1 A_j
            custos_reduzidos = c - cB @ B_inv_A
            custos_reduzidos[base] = 0.0

            # Regra de Bland: menor índice com custo reduzido positivo.
            candidatos = [
                j
                for j in range(n)
                if j not in base and custos_reduzidos[j] > self.tol
            ]

            if not candidatos:
                x = np.zeros(n, dtype=float)
                x[base] = xB
                z = float(c @ x)

                return "optimal", x, z, base, iteracao

            entra = min(candidatos)
            direcao = B_inv_A[:, entra]

            razoes = [
                (xB[i] / direcao[i], i)
                for i in range(m)
                if direcao[i] > self.tol
            ]

            if not razoes:
                return "unbounded", None, None, base, iteracao

            theta = min(valor for valor, _ in razoes)

            empatados = [
                i
                for valor, i in razoes
                if abs(valor - theta) <= 1e-10
            ]

            # Bland também no desempate da variável que sai.
            sai_linha = min(empatados, key=lambda i: base[i])

            base[sai_linha] = entra

        return "iteration_limit", None, None, base, self.max_iteracoes

    # ------------------------------------------------------------------

    def _remover_artificiais(
        self,
        A,
        b,
        base,
        artificiais
    ):
        """
        Remove variáveis artificiais após a Fase I.

        Estratégia:

        1. transforma o sistema para a forma canônica da base atual;
        2. tenta retirar artificiais básicas por pivotamento;
        3. remove linhas redundantes apenas no sistema transformado;
        4. elimina definitivamente as colunas artificiais.
        """

        A = np.asarray(
            A,
            dtype=float
        ).copy()

        b = np.asarray(
            b,
            dtype=float
        ).copy()

        base = list(base)

        conjunto_artificiais = set(
            artificiais
        )

        # ========================================================
        # 1. TRANSFORMA PARA A BASE CANÔNICA ATUAL
        # ========================================================

        B = A[:, base]

        try:
            A_canonico = np.linalg.solve(
                B,
                A
            )

            b_canonico = np.linalg.solve(
                B,
                b
            )

        except np.linalg.LinAlgError as erro:
            raise RuntimeError(
                "Não foi possível canonicalizar a base após a Fase I."
            ) from erro

        A_canonico[
            np.abs(A_canonico) < self.tol
        ] = 0.0

        b_canonico[
            np.abs(b_canonico) < self.tol
        ] = 0.0

        # ========================================================
        # 2. REMOVE ARTIFICIAIS QUE AINDA ESTÃO NA BASE
        # ========================================================

        i = 0

        while i < len(base):

            variavel_basica = base[i]

            if variavel_basica not in conjunto_artificiais:
                i += 1
                continue

            candidatos = [
                j
                for j in range(
                    A_canonico.shape[1]
                )
                if (
                    j not in conjunto_artificiais
                    and
                    j not in base
                    and
                    abs(
                        A_canonico[i, j]
                    ) > self.tol
                )
            ]

            if candidatos:

                entra = max(
                    candidatos,
                    key=lambda j: (
                        abs(
                            A_canonico[i, j]
                        ),
                        -j
                    )
                )

                pivo = A_canonico[
                    i,
                    entra
                ]

                A_canonico[i, :] /= pivo
                b_canonico[i] /= pivo

                for linha in range(
                    A_canonico.shape[0]
                ):

                    if linha == i:
                        continue

                    fator = A_canonico[
                        linha,
                        entra
                    ]

                    if abs(fator) > self.tol:

                        A_canonico[linha, :] -= (
                            fator
                            *
                            A_canonico[i, :]
                        )

                        b_canonico[linha] -= (
                            fator
                            *
                            b_canonico[i]
                        )

                base[i] = entra

                A_canonico[
                    np.abs(A_canonico) < self.tol
                ] = 0.0

                b_canonico[
                    np.abs(b_canonico) < self.tol
                ] = 0.0

                i += 1

            else:

                if abs(
                    b_canonico[i]
                ) > 1e-7:

                    raise RuntimeError(
                        "Variável artificial positiva após "
                        "uma Fase I considerada factível."
                    )

                A_canonico = np.delete(
                    A_canonico,
                    i,
                    axis=0
                )

                b_canonico = np.delete(
                    b_canonico,
                    i
                )

                base.pop(i)

        # ========================================================
        # 3. REMOVE AS COLUNAS ARTIFICIAIS
        # ========================================================

        colunas_mantidas = [
            j
            for j in range(
                A_canonico.shape[1]
            )
            if j not in conjunto_artificiais
        ]

        mapa_colunas = {
            indice_antigo: indice_novo
            for indice_novo, indice_antigo
            in enumerate(
                colunas_mantidas
            )
        }

        A_sem_artificiais = A_canonico[
            :,
            colunas_mantidas
        ]

        base_nova = [
            mapa_colunas[j]
            for j in base
        ]

        # ========================================================
        # 4. VERIFICAÇÃO DE SEGURANÇA DA BASE
        # ========================================================

        if base_nova:

            B_final = A_sem_artificiais[
                :,
                base_nova
            ]

            posto = np.linalg.matrix_rank(
                B_final
            )

            if posto < len(
                base_nova
            ):

                raise RuntimeError(
                    "A base obtida após a remoção das "
                    "variáveis artificiais é singular."
                )

        return (
            A_sem_artificiais,
            b_canonico,
            base_nova,
            colunas_mantidas
        )
    
def verificar_restricoes(A, b, operadores, x, tolerancia=1e-7):
    """
    Utilitário independente para verificar se uma solução satisfaz
    cada restrição do modelo original.
    """

    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    x = np.asarray(x, dtype=float)

    lhs = A @ x
    resultados = []

    for i, op in enumerate(operadores):
        if op == "<=":
            ok = lhs[i] <= b[i] + tolerancia
        elif op == ">=":
            ok = lhs[i] >= b[i] - tolerancia
        else:
            ok = abs(lhs[i] - b[i]) <= tolerancia

        resultados.append(
            {
                "restricao": i + 1,
                "lado_esquerdo": float(lhs[i]),
                "operador": op,
                "lado_direito": float(b[i]),
                "satisfeita": bool(ok),
            }
        )

    return resultados

