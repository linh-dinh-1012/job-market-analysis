.PHONY: help docs html clean

help:
	@echo "Commandes disponibles :"
	@echo "  make docs    - Générer la documentation Sphinx (HTML)"
	@echo "  make html    - Alias de make docs"
	@echo "  make clean   - Nettoyer les fichiers générés"

html: docs

docs:
	sphinx-build -b html source _build/html

clean:
	rm -rf _build
