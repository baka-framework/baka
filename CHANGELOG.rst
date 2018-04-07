Baka Changelog
===============

Di sini Anda bisa melihat daftar lengkap perubahan di antara setiap rilis Baka framework.



Version 0.4
------------

Major release, unreleased codename ``aiko``

- add docs, `Bakadocs`_ untuk memudahkan cara menggunakan.
- Remove ``app.scan()``, tidak perlu menggunakan fitur scan dari venusian.
- Dependency less venusian, ``venusian.attach(wrapped, callback, 'pyramid', depth=depth)`` menghilangkan dependency venusian di feature route.
- add pyramid ``authenticate and authorization`` policy settings.
- add error handler function, ``error_handler(code)`` route, dengan memasukan http code untuk me-redirect ke handler yang sudah di buat.
- add exception handler function, ``exception_handler`` route, default code 509 dengan pesan status berisi error exception `(resiliency)` methodologi.
- add ``trafaret`` validator, default False untuk `config_schema` values.
- add directive ``add_config_validator``, untuk schema trafaret validator.
- add directive ``get_settings_validator``, untuk menvalidasi trafaret validator.
- custom JSON renderer, ``JSONEncoder``, type object dump (ObjectId untuk mongodb id); uuid type; datetime type; EnumInt Type; enum


.. _Bakadocs: http://baka-framework.readthedocs.io/en/latest/
