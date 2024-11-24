from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os
import hashlib
from datetime import datetime
import zipfile
from fastapi.responses import FileResponse

app = FastAPI()

CSV_FILE = "voos.csv"

HEADER = ["id_voo", "numero_voo", "cia", "origem", 
          "destino", "horario_partida", "horario_chegada", 
          "id_aeronave", "status"]

class Voo(BaseModel):
    id_voo: int
    numero_voo: int
    cia: str
    origem: str
    destino: str
    horario_partida: datetime
    horario_chegada: datetime
    id_aeronave: int
    status: str

@app.get("/")
def read_root():
    return {"message": "Serviço de Gerenciamento de Voos"}

def verificar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(HEADER)

# Funcionalidade 1: Inserir dados no CSV
@app.post("/voos/")
def inserir_voo(voo: Voo):
    verificar_csv()

    try:
        with open(CSV_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                voo.id_voo, voo.numero_voo, voo.cia, voo.origem,
                voo.destino, voo.horario_partida.isoformat(),
                voo.horario_chegada.isoformat(), voo.id_aeronave, voo.status
            ])
        return {"message": "Voo inserido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar dados: {e}")

# Funcionalidade 2: Retornar todos os dados cadastrados no CSV
@app.get("/voos/")
def listar_voos():
    verificar_csv()
    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            voos = [
                {key: int(value) if key in ["id_voo", "numero_voo", "id_aeronave"] else value
                 for key, value in row.items()}
                for row in reader
            ]
        return voos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar voos: {e}")

# Funcionalidade 5: Compactar o arquivo CSV em um ZIP
@app.get("/voos/compactar")
def compactar_csv():
    verificar_csv()
    
    zip_file = CSV_FILE.replace("voos.csv", "voos.zip")
    
    try:
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(CSV_FILE, os.path.basename(CSV_FILE))

        return FileResponse(
            path=zip_file,
            media_type="application/zip",
            filename=os.path.basename(zip_file),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao compactar arquivo: {e}")

# Funcionalidade 3: Obter um registro específico pelo ID
@app.get("/voos/{id_voo}")
def obter_voo(id_voo: int):
    verificar_csv()
    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["id_voo"]) == id_voo:
                    return row
        raise HTTPException(status_code=404, detail="Voo não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar voo: {e}")

# Funcionalidade 3: Atualizar um registro específico pelo ID
@app.put("/voos/{id_voo}")
def atualizar_voo(id_voo: int, voo_atualizado: Voo):
    verificar_csv()
    try:
        atualizado = False
        voos = []

        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file, fieldnames=HEADER)
            next(reader, None)
            for row in reader:
                if int(row["id_voo"]) == id_voo:
                    voos.append({
                        "id_voo": voo_atualizado.id_voo,
                        "numero_voo": voo_atualizado.numero_voo,
                        "cia": voo_atualizado.cia,
                        "origem": voo_atualizado.origem,
                        "destino": voo_atualizado.destino,
                        "horario_partida": voo_atualizado.horario_partida.isoformat(),
                        "horario_chegada": voo_atualizado.horario_chegada.isoformat(),
                        "id_aeronave": voo_atualizado.id_aeronave,
                        "status": voo_atualizado.status
                    })
                    atualizado = True
                else:
                    voos.append(row)

        if not atualizado:
            raise HTTPException(status_code=404, detail="Voo não encontrado.")

        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(voos)

        return {"message": "Voo atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar voo: {e}")

# Funcionalidade 3: Excluir um registro específico pelo ID
@app.delete("/voos/{id_voo}")
def deletar_voo(id_voo: int):
    verificar_csv()
    try:
        voos = []
        deletado = False
        
        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["id_voo"]) == id_voo:
                    deletado = True
                else:
                    voos.append(row)

        if not deletado:
            raise HTTPException(status_code=404, detail="Voo não encontrado.")

        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(voos)

        return {"message": "Voo deletado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar voo: {e}")

# Funcionalidade 4: Contar o número de registros no CSV
@app.get("/contar_registros")
def contar_registros():
    verificar_csv()
    if os.stat(CSV_FILE).st_size == 0:
        return {"Total de Registros": 0}
    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            count = sum(1 for _ in reader)
        return {"Total de Registros": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar registros: {e}")

# Funcionalidade 6: Retornar o hash SHA256 do arquivo CSV
@app.get("/hash/")
def obter_hash():
    verificar_csv()
    try:
        with open(CSV_FILE, "rb") as file:
            sha256_hash = hashlib.sha256(file.read()).hexdigest()
        return {"SHA256": sha256_hash}
    except FileNotFoundError:
        return {"error": "Arquivo CSV não encontrado."}
    except Exception as e:
        return {"error": f"Erro ao calcular hash: {str(e)}"}
