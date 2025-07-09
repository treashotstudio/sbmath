import os
import re
import PySimpleGUI as sg
from PyPDF2 import PdfMerger

sg.theme("SystemDefault")

layout = [
    [sg.Text("📂 PDF가 저장된 폴더를 선택하세요")],
    [sg.InputText(key="-FOLDER-"), sg.FolderBrowse("찾아보기")],
    [sg.Button("PDF 병합 실행", key="-MERGE-"), sg.Exit("종료")]
]

window = sg.Window("PDF 자동 병합기", layout)

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "종료"):
        break

    if event == "-MERGE-":
        folder_path = values["-FOLDER-"]
        if not folder_path or not os.path.isdir(folder_path):
            sg.popup_error("❗ 올바른 폴더를 선택해주세요.")
            continue

        output_folder = os.path.join(folder_path, "merged")
        os.makedirs(output_folder, exist_ok=True)

        pdf_dict = {}

        # 📁 PDF 파일 분류
        for filename in os.listdir(folder_path):
            if not filename.endswith(".pdf"):
                continue
            name_match = re.match(r"^([가-힣]{2,4})\.pdf$", filename)
            if name_match:
                name = name_match.group(1)
                pdf_dict.setdefault(name, {"main": None, "others": []})
                pdf_dict[name]["main"] = os.path.join(folder_path, filename)
            else:
                partial_match = re.match(r"^([가-힣]{2,4})_", filename)
                if partial_match:
                    name = partial_match.group(1)
                    pdf_dict.setdefault(name, {"main": None, "others": []})
                    pdf_dict[name]["others"].append(os.path.join(folder_path, filename))

        success_count = 0
        skip_count = 0
        skipped_names = []

        # 🔁 병합
        for name, files in pdf_dict.items():
            main_pdf = files["main"]
            others = sorted(files["others"])

            # 병합 조건: main + 관련 파일 최소 1개
            if not main_pdf or len(others) == 0:
                skip_count += 1
                skipped_names.append(name)
                continue

            merger = PdfMerger()
            merger.append(main_pdf)
            for pdf_file in others:
                merger.append(pdf_file)

            output_path = os.path.join(output_folder, f"{name}.pdf")
            merger.write(output_path)
            merger.close()
            success_count += 1

        # ✅ 결과 출력
        message = f"✅ 병합 완료!\n\n완료된 파일: {success_count}개\n스킵된 이름: {skip_count}개"
        if skipped_names:
            message += "\n\n❌ 병합되지 않은 이름:\n- " + "\n- ".join(skipped_names)
        message += "\n\n📁 병합 결과는 'merged' 폴더에 저장되었습니다."

        sg.popup(message)

window.close()