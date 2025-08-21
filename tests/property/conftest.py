from hypothesis import settings, HealthCheck

# Perfil dedicado para property-based tests deste diretório
settings.register_profile(
    "property",
    deadline=None,  # evitar flakiness por timeouts
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.function_scoped_fixture,
        HealthCheck.filter_too_much,
        HealthCheck.data_too_large,
    ],
    max_examples=30,
)
settings.load_profile("property")
