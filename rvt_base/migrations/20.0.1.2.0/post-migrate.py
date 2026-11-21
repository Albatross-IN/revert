def migrate(cr, version):
    """Bedrooms beside a master bedroom are numbered from 2 (the preset data is noupdate)."""
    cr.execute("""
        UPDATE rvt_site_preset_line l
           SET number_from = 2
          FROM ir_model_data d
         WHERE d.model = 'rvt.site.preset.line' AND d.res_id = l.id AND d.module = 'rvt_base'
           AND d.name IN ('preset_3bhk_bedroom', 'preset_4bhk_bedroom')
    """)
