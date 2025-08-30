class Roles:
    SUPERADMIN = "superadmin"
    EMPRESA = "empresa"
    EMPLEADO = "empleado"

    @classmethod
    def get_roles(cls):
        return [cls.SUPERADMIN, cls.EMPRESA, cls.EMPLEADO]
