from weasyprint import HTML

html = "<h1>Hello WeasyPrint!</h1><p>Funziona 🎉</p>"
HTML(string=html).write_pdf("test_weasy.pdf")
print("PDF generato: test_weasy.pdf")