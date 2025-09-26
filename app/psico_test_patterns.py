PSICOMETRIC_TESTS = {
    # TEA Ediciones
    "WISC": [
        r"\bWISC[\s-]*[IVX]*\b", r"Wechsler.*Inteligencia.*Ni[nñ]os", r"WISc", r"WlSC", r"WISC-IV", r"WISC V"
    ],
    "WAIS": [
        r"\bWAIS[\s-]*[IVX]*\b", r"Wechsler.*Inteligencia.*Adult[oa]s", r"WAlS", r"WAIS-III", r"WAIS IV"
    ],
    "WPPSI": [
        r"\bWPPSI[\s-]*[IVX]*\b", r"Wechsler.*Preescolar.*Primaria", r"WPPSl", r"WPPSI-III", r"WPPSI IV"
    ],
    "WASI": [
        r"\bWASI\b", r"Wechsler.*Abreviada", r"WASI-II"
    ],
    "K-BIT": [
        r"\bK[-\s]?BIT\b", r"Kaufman.*brev[eé]", r"KBIT", r"K BIT"
    ],
    "Raven": [
        r"\bRaven\b", r"Matrices.*Progresivas.*Raven", r"Raven Matrices", r"Raven Matric[ei]s", r"RAVEN"
    ],
    "SENA": [
        r"\bSENA\b", r"Sistema.*Evaluaci[oó]n.*Ni[nñ]os.*Adolescentes"
    ],
    "BASC": [
        r"\bBASC\b", r"BASC-II", r"Sistema.*Evaluaci[oó]n.*Comportamiento", r"BASC[\s-]*II"
    ],
    "BDI": [
        r"\bBDI\b", r"Beck.*Depresi[oó]n.*Inventario", r"BDI-II"
    ],
    "BAI": [
        r"\bBAI\b", r"Beck.*Ansiedad.*Inventario"
    ],
    "STAI": [
        r"\bSTAI\b", r"Spielberger.*Ansiedad"
    ],
    "STAXI": [
        r"\bSTAXI\b", r"Spielberger.*Expresi[oó]n.*Ira"
    ],
    "MMPI": [
        r"\bMMPI[\s-]*[IVX]*\b", r"Minnesota.*Multiphasic.*Personality.*Inventory", r"MMPI-2"
    ],
    "MCMI": [
        r"\bMCMI[\s-]*[IVX]*\b", r"Millon.*Clinical.*Multiaxial.*Inventory", r"MCMI-III"
    ],
    "TPT": [
        r"\bTPT\b", r"Test.*Percepci[oó]n.*Tem[aá]tica"
    ],
    "TDAH": [
        r"\bTDAH\b", r"Trastorno.*Deficit.*Atenc[ií]on.*Hiperactividad"
    ],
    "PROLEC": [
        r"\bPROLEC\b", r"Proceso.*Lectura"
    ],
    "PROESC": [
        r"\bPROESC\b", r"Proceso.*Escritura"
    ],
    "PROLEXIA": [
        r"\bPROLEXIA\b", r"Proceso.*Lexia"
    ],
    "PRODISCAT": [
        r"\bPRODISCAT[\s-]*2?\b", r"Proceso.*Discalculia"
    ],
    "TAVEC": [
        r"\bTAVEC[\s-]*2?\b", r"Test.*Aprendizaje.*Verbal.*España.*Complutense"
    ],
    "NEPSY": [
        r"\bNEPSY[\s-]*II?\b", r"Neuropsychological.*Assessment", r"NEPSY-II"
    ],
    "D2": [
        r"\bD2[\s-]*R?\b", r"Test.*Atenci[oó]n.*D2", r"D2-R"
    ],
    "Luria": [
        r"\bLuria\b", r"Neuropsicol[oó]gico.*Luria"
    ],
    "EFAI": [
        r"\bEFAI\b", r"Escala.*Funcionamiento.*Adaptativo"
    ],
    "EFR": [
        r"\bEFR\b", r"Escala.*Funcionamiento.*Resiliencia"
    ],
    "ENFEN": [
        r"\bENFEN\b", r"Evaluaci[oó]n.*Funciones.*Ejecutivas.*Ni[nñ]os"
    ],
    "EPC": [
        r"\bEPC\b", r"Escala.*Pensamiento.*Creativo"
    ],
    "Conners": [
        r"\bConners\b", r"Escala.*Conners.*TDAH", r"Conners-3", r"Conners-4"
    ],

    # Pearson Clinical
    "CELF": [
        r"\bCELF[\s-]*5?\b", r"Evaluaci[oó]n.*Cl[ií]nica.*Fundamentos.*Lenguaje", r"CELF-5"
    ],
    "WIAT": [
        r"\bWIAT\b", r"Wechsler.*Achievement.*Test", r"WIAT-III"
    ],
    "WRAML": [
        r"\bWRAML\b", r"Wechsler.*Memory.*Scale"
    ],
    "WRAVMA": [
        r"\bWRAVMA\b", r"Wide.*Range.*Assessment.*Visual.*Motor.*Abilities"
    ],
    "K-ABC": [
        r"\bK[-\s]?ABC\b", r"Kaufman.*Assessment.*Battery", r"KABC-II"
    ],
    "KTEA": [
        r"\bKTEA\b", r"Kaufman.*Test.*Educational.*Achievement"
    ],
    "MABC": [
        r"\bMABC\b", r"Movement.*Assessment.*Battery.*Children", r"MABC-2"
    ],
    "Vineland": [
        r"\bVineland\b", r"Vineland.*Adaptive.*Behavior.*Scales", r"Vineland-II"
    ],
    "Bayley": [
        r"\bBayley\b", r"Bayley.*Escalas.*Desarrollo.*Infantil", r"Bayley-III"
    ],
    "PPVT": [
        r"\bPPVT\b", r"Peabody.*Picture.*Vocabulary.*Test"
    ],
    "EVT": [
        r"\bEVT\b", r"Expressive.*Vocabulary.*Test"
    ],

    # COP (genérico, para informes que mencionan COP)
    "COP": [
        r"\bCOP\b", r"Consejo.*General.*Psicolog[ií]a", r"Inventario COP", r"Escala COP"
    ]
}
