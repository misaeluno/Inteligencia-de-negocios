import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Calcula columnas extra dadas la matriz de eficacias pera determinar resistencias, inmunidades, debilidades y vulnerabilidad de un pokémon
def defense(type1, type2, eff):
    if pd.isna(type2):  # Revisar si el tipo 2 es NaN
        defenses = eff.loc[:, type1]
    else:
        defenses = (
            eff.loc[:, type1] * eff.loc[:, type2]
        )  # Multiplicar las eficacias de los tipos

    weaknesses = (defenses > 1).sum()
    resistances = (defenses < 1).sum()
    immunities = (defenses == 0).sum()
    vulnerability = defenses.sum()

    return weaknesses, resistances, immunities, vulnerability


# Calcula columnas extra dadas la matriz de eficacias para poder determinar si un pokemon es super débil
def super(type1, type2, eff):
    if pd.isna(type2):
        return False

    combined = eff.loc[:, type1] * eff.loc[:, type2]
    return (combined >= 4).any(), (combined <= 0.25).any()


def main():
    pkmn = pd.read_csv("Pokemon.csv")
    pkmn["Pseudo-Legendary"] = np.where(
        (pkmn["Total"] == 600) & (~pkmn["Legendary"]), True, False
    )
    # Filtro las mega evoluciones
    pkmn = pkmn[~pkmn["Name"].str.contains("Mega", na=False)].reset_index(drop=True)
    print(pkmn)

    # Cargo la matriz de eficacias
    eff = pd.read_csv("effMat.csv")
    eff = eff.set_index("Attacking")
    print(eff)

    defensive_stats = pkmn.apply(
        lambda row: defense(row["Type 1"], row["Type 2"], eff),
        axis=1,
        result_type="expand",
    )
    defensive_stats.columns = [
        "Weaknesses",
        "Resistances",
        "Immunities",
        "Vulnerability",
    ]
    pkmn = pd.concat([pkmn, defensive_stats], axis=1)

    super_stats = pkmn.apply(
        lambda row: super(row["Type 1"], row["Type 2"], eff),
        axis=1,
        result_type="expand",
    )
    super_stats.columns = [
        "Super Weaknesses",
        "Super Resistances",
    ]
    pkmn = pd.concat([pkmn, super_stats], axis=1)
    print(pkmn)

    vulnerable = pkmn.nlargest(10, "Vulnerability")[
        ["Name", "Type 1", "Type 2", "Vulnerability", "Weaknesses", "Total"]
    ]
    print(vulnerable)

    weaknesses = pkmn.nlargest(10, "Weaknesses")[
        ["Name", "Type 1", "Type 2", "Weaknesses", "Vulnerability", "Total"]
    ]
    print(weaknesses)

    resistances = pkmn.nlargest(10, "Resistances")[
        [
            "Name",
            "Type 1",
            "Type 2",
            "Resistances",
            "Vulnerability",
            "Immunities",
            "Total",
        ]
    ]
    print(resistances)

    blitz = pkmn.nlargest(10, "Speed")[
        ["Name", "Type 1", "Type 2", "Speed", "Total", "Vulnerability"]
    ]
    print(blitz)

    # Exporto todo como Excel
    with pd.ExcelWriter("pkmn.xlsx") as writer:
        pkmn.to_excel(writer, sheet_name="pkmn", index=False)
        eff.to_excel(writer, sheet_name="matrix", index=False)
        vulnerable.to_excel(writer, sheet_name="vul", index=False)
        weaknesses.to_excel(writer, sheet_name="weak", index=False)
        resistances.to_excel(writer, sheet_name="resist", index=False)
        blitz.to_excel(writer, sheet_name="blitz", index=False)

    plt.figure(figsize=(12, 8))

    # Graficar puntos
    vuln_scatter = plt.scatter(
        vulnerable["Vulnerability"],
        vulnerable["Total"],
        alpha=0.6,
        color="red",
        label="Most Vulnerable",
    )
    weak_scatter = plt.scatter(
        weaknesses["Vulnerability"],
        weaknesses["Total"],
        alpha=0.6,
        color="blue",
        label="Most Weaknesses",
    )
    resist_scatter = plt.scatter(
        resistances["Vulnerability"],
        resistances["Total"],
        alpha=0.6,
        color="green",
        label="Most Resistances",
    )
    blitz_scatter = plt.scatter(
        blitz["Vulnerability"],
        blitz["Total"],
        alpha=0.6,
        color="purple",
        label="Fastest",
    )

    # Añado etiquetas
    for i, row in vulnerable.iterrows():
        plt.annotate(
            row["Name"],
            (row["Vulnerability"], row["Total"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
            color="red",
        )

    # Añado etiquetas
    for i, row in weaknesses.iterrows():
        plt.annotate(
            row["Name"],
            (row["Vulnerability"], row["Total"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
            color="blue",
        )

    # Añado etiquetas
    for i, row in resistances.iterrows():
        plt.annotate(
            row["Name"],
            (row["Vulnerability"], row["Total"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
            color="green",
        )

    # Añado etiquetas
    for i, row in blitz.iterrows():
        plt.annotate(
            row["Name"],
            (row["Vulnerability"], row["Total"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.8,
            color="purple",
        )

    plt.xlabel("Defensive Vulnerability Score")
    plt.ylabel("Total Stats")
    plt.title("Pokémon: Defensive Vulnerability vs Overall Power")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
