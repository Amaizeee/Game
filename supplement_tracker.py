import json
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List

DATA_FILE = Path("supplement_data.json")
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


@dataclass
class Supplement:
    name: str
    dosage: str
    frequency: str
    notes: str = ""


@dataclass
class IntakeLog:
    supplement_name: str
    taken_at: str
    quantity: str
    notes: str = ""


def load_data() -> Dict[str, List[dict]]:
    if not DATA_FILE.exists():
        return {"supplements": [], "logs": []}
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(data: Dict[str, List[dict]]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def prompt(message: str) -> str:
    return input(message).strip()


def add_supplement(data: Dict[str, List[dict]]) -> None:
    name = prompt("Nom du complément: ")
    dosage = prompt("Dosage (ex: 500 mg): ")
    frequency = prompt("Fréquence (ex: 1 fois/jour): ")
    notes = prompt("Notes (optionnel): ")
    supplement = Supplement(name=name, dosage=dosage, frequency=frequency, notes=notes)
    data["supplements"].append(asdict(supplement))
    save_data(data)
    print("✅ Complément ajouté.")


def list_supplements(data: Dict[str, List[dict]]) -> None:
    supplements = data.get("supplements", [])
    if not supplements:
        print("Aucun complément enregistré.")
        return
    print("\n--- Compléments ---")
    for index, item in enumerate(supplements, start=1):
        print(
            f"{index}. {item['name']} | Dosage: {item['dosage']} | Fréquence: {item['frequency']}"
        )
        if item.get("notes"):
            print(f"   Notes: {item['notes']}")


def log_intake(data: Dict[str, List[dict]]) -> None:
    supplements = data.get("supplements", [])
    if not supplements:
        print("Ajoutez d'abord un complément.")
        return
    name = prompt("Nom du complément pris: ")
    quantity = prompt("Quantité prise (ex: 1 capsule): ")
    default_date = date.today().strftime(DATE_FORMAT)
    default_time = datetime.now().strftime(TIME_FORMAT)
    date_str = prompt(f"Date ({default_date}): ") or default_date
    time_str = prompt(f"Heure ({default_time}): ") or default_time
    notes = prompt("Notes (optionnel): ")
    taken_at = f"{date_str} {time_str}"
    log_entry = IntakeLog(
        supplement_name=name,
        taken_at=taken_at,
        quantity=quantity,
        notes=notes,
    )
    data["logs"].append(asdict(log_entry))
    save_data(data)
    print("✅ Prise enregistrée.")


def show_logs(data: Dict[str, List[dict]]) -> None:
    logs = data.get("logs", [])
    if not logs:
        print("Aucune prise enregistrée.")
        return
    print("\n--- Journal des prises ---")
    for entry in logs:
        print(
            f"{entry['taken_at']} | {entry['supplement_name']} | Quantité: {entry['quantity']}"
        )
        if entry.get("notes"):
            print(f"   Notes: {entry['notes']}")


def daily_summary(data: Dict[str, List[dict]]) -> None:
    target_date = prompt("Date à résumer (AAAA-MM-JJ, vide pour aujourd'hui): ")
    if not target_date:
        target_date = date.today().strftime(DATE_FORMAT)
    logs = data.get("logs", [])
    summary: Dict[str, int] = {}
    for entry in logs:
        if entry["taken_at"].startswith(target_date):
            summary[entry["supplement_name"]] = summary.get(entry["supplement_name"], 0) + 1
    if not summary:
        print("Aucune prise trouvée pour cette date.")
        return
    print(f"\n--- Résumé du {target_date} ---")
    for name, count in summary.items():
        print(f"{name}: {count} prise(s)")


def menu() -> None:
    data = load_data()
    actions = {
        "1": ("Ajouter un complément", add_supplement),
        "2": ("Lister les compléments", list_supplements),
        "3": ("Enregistrer une prise", log_intake),
        "4": ("Voir le journal des prises", show_logs),
        "5": ("Résumé quotidien", daily_summary),
        "6": ("Quitter", None),
    }
    while True:
        print("\n=== Suivi des compléments alimentaires ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        choice = prompt("Choisissez une option: ")
        action = actions.get(choice)
        if not action:
            print("Option invalide.")
            continue
        if choice == "6":
            print("Au revoir !")
            break
        action[1](data)


if __name__ == "__main__":
    menu()
