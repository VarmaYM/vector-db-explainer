.PHONY: test

test:
	@python3 tools/check_doc.py
	@python3 tools/check_animation.py
	@python3 -m py_compile tools/check_doc.py tools/check_animation.py
