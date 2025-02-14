from cProfile import label
from django import forms
from django.conf import settings

from django.utils.translation import gettext as _

from circuits.models import Circuit
from dcim.models import Device, Site, SiteGroup, Region, DeviceRole, Location, Rack, Manufacturer, DeviceType, Platform, PowerPanel, PowerFeed

from django import forms
from dcim.choices import DeviceStatusChoices, DeviceAirflowChoices
from tenancy.models import TenantGroup, Tenant
from extras.models import ConfigTemplate
from extras.forms import LocalConfigContextFilterForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from django.conf import settings
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import (
    TagFilterField,
    DynamicModelMultipleChoiceField
)

from netbox_topology_views.models import IndividualOptions, CoordinateGroup, Coordinate, CircuitCoordinate, PowerPanelCoordinate, PowerFeedCoordinate

class DeviceFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    default_renderer = forms.renderers.DjangoTemplates()
    model = Device
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Options'), (
            'group', 'save_coords', 'show_unconnected', 'show_cables', 'show_logical_connections',
            'show_single_cable_logical_conns', 'show_neighbors', 'show_circuit', 'show_power', 'show_wireless',
        )),
        (_('Device'), ('id',)),        
        (_('Location'), ('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id')),
        (_('Operation'), ('status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address')),
        (_('Hardware'), ('manufacturer_id', 'device_type_id', 'platform_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
        (_('Contacts'), ('contact', 'contact_role', 'contact_group')),
        (_('Components'), (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports',
        )),
        (_('Miscellaneous'), (
            'has_primary_ip', 'has_oob_ip', 'virtual_chassis_member', 'config_template_id', 'local_context_data',
        )),
    )
    group = forms.ModelChoiceField(
        queryset=CoordinateGroup.objects.all(),
        required=False,
        label=_('Coordinate group'),
    )
    id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device'),
        query_params={
            'location_id': '$location_id',
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
            'site_id': '$site_id',
            'role_id': '$role_id',
            'contact': '$contact',
            'contact_role': '$contact_role',
            'contact_group': '$contact_group',
        },
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(), 
        required=False, 
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site Group'),
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
            'site_id': '$site_id',
        },
        label=_('Location'),
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Rack'),
    )
    status = forms.MultipleChoiceField(
        choices=DeviceStatusChoices, 
        required=False, 
        label=_('Device Status')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(), 
        required=False, 
        label=_('Role')
    )
    airflow = forms.MultipleChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    serial = forms.CharField(
        label=_('Serial'),
        required=False
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        required=False
    )
    mac_address = forms.CharField(
        required=False,
        label=_('MAC address')
    )    
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Model')
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label=_('Platform')
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console server ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label=_('Has power ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label=_('Has power outlets'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label=_('Has interfaces'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label=_('Has pass-through ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    config_template_id = DynamicModelMultipleChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False,
        label=_('Config template')
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label=_('Has a primary IP'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    has_oob_ip = forms.NullBooleanField(
        required=False,
        label='Has an OOB IP',
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label=_('Virtual chassis member'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )

    tag = TagFilterField(model)

    # options
    save_coords = forms.BooleanField(
        label=_('Save Coordinates'),
        required=False,
        disabled=(not settings.PLUGINS_CONFIG['netbox_topology_views']['allow_coordinates_saving'] or settings.PLUGINS_CONFIG['netbox_topology_views']['always_save_coordinates']),
        initial=(settings.PLUGINS_CONFIG['netbox_topology_views']['always_save_coordinates'])
    )
    show_unconnected = forms.BooleanField(
        label=_('Show Unconnected'), required=False, initial=False
    )
    show_cables = forms.BooleanField(
        label =_('Show Cables'), required=False, initial=False
    )
    show_logical_connections = forms.BooleanField(
        label =_('Show Logical Connections'), required=False, initial=False
    )
    show_single_cable_logical_conns = forms.BooleanField(
        label =_('Show redundant Cable and Logical Connection'), required=False, initial=False
    )
    show_neighbors = forms.BooleanField(
        label =_('Show Neighbors'), required=False, initial=False
    )
    show_circuit = forms.BooleanField(
        label=_('Show Circuit Terminations'), required=False, initial=False
    )
    show_power = forms.BooleanField(
        label=_('Show Power Feeds'), required=False, initial=False
    )
    show_wireless = forms.BooleanField(
        label =_('Show Wireless Links'), required=False, initial=False
    )

class CoordinateGroupsForm(NetBoxModelForm):
    fieldsets = (
        ('Group Details', ('name', 'description')),
    )

    class Meta:
        model = CoordinateGroup
        fields = ('name', 'description')

class CoordinateGroupsImportForm(NetBoxModelImportForm):
    class Meta:
        model = CoordinateGroup
        fields = ('name', 'description')

class CircuitCoordinatesForm(NetBoxModelForm):
    fieldsets = (
        ('CircuitCoordinate', ('group', 'device', 'x', 'y')),
    )

    class Meta:
        model = CircuitCoordinate
        fields = ('group', 'device', 'x', 'y')

class PowerPanelCoordinatesForm(NetBoxModelForm):
    fieldsets = (
        ('PowerPanel', ('group', 'device', 'x', 'y')),
    )

    class Meta:
        model = PowerPanelCoordinate
        fields = ('group', 'device', 'x', 'y')

class PowerFeedCoordinatesForm(NetBoxModelForm):
    fieldsets = (
        ('PowerFeedCoordinate', ('group', 'device', 'x', 'y')),
    )

    class Meta:
        model = PowerFeedCoordinate
        fields = ('group', 'device', 'x', 'y')

class CoordinatesForm(NetBoxModelForm):
    fieldsets = (
        ('Coordinate', ('group', 'device', 'x', 'y')),
    )

    class Meta:
        model = Coordinate
        fields = ('group', 'device', 'x', 'y')

class CircuitCoordinatesImportForm(NetBoxModelImportForm):
    class Meta:
        model = CircuitCoordinate
        fields = ('group', 'device', 'x', 'y')

class PowerPanelCoordinatesImportForm(NetBoxModelImportForm):
    class Meta:
        model = PowerPanelCoordinate
        fields = ('group', 'device', 'x', 'y')

class PowerFeedCoordinatesImportForm(NetBoxModelImportForm):
    class Meta:
        model = PowerFeedCoordinate
        fields = ('group', 'device', 'x', 'y')

class CoordinatesImportForm(NetBoxModelImportForm):
    class Meta:
        model = Coordinate
        fields = ('group', 'device', 'x', 'y')

class CircuitCoordinatesFilterForm(NetBoxModelFilterSetForm):
    model = CircuitCoordinate
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('CircuitCoordinates', ('group', 'device', 'x', 'y'))
    )

    group = forms.ModelMultipleChoiceField(
        queryset=CoordinateGroup.objects.all(),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False
    )

    x = forms.IntegerField(
        required=False
    )

    y = forms.IntegerField(
        required=False
    )

class PowerPanelCoordinatesFilterForm(NetBoxModelFilterSetForm):
    model = PowerPanelCoordinate
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('PowerPanelCoordinates', ('group', 'device', 'x', 'y'))
    )

    group = forms.ModelMultipleChoiceField(
        queryset=CoordinateGroup.objects.all(),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False
    )

    x = forms.IntegerField(
        required=False
    )

    y = forms.IntegerField(
        required=False
    )

class PowerFeedCoordinatesFilterForm(NetBoxModelFilterSetForm):
    model = Coordinate
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('PowerFeedCoordinates', ('group', 'device', 'x', 'y'))
    )

    group = forms.ModelMultipleChoiceField(
        queryset=CoordinateGroup.objects.all(),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        required=False
    )

    x = forms.IntegerField(
        required=False
    )

    y = forms.IntegerField(
        required=False
    )

class CoordinatesFilterForm(NetBoxModelFilterSetForm):
    model = Coordinate
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Coordinates', ('group', 'device', 'x', 'y'))
    )

    group = forms.ModelMultipleChoiceField(
        queryset=CoordinateGroup.objects.all(),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )

    x = forms.IntegerField(
        required=False
    )

    y = forms.IntegerField(
        required=False
    )

class IndividualOptionsForm(NetBoxModelForm):
    fieldsets = (
        (
            None,
            (
                'user_id',
                'ignore_cable_type',
                'preselected_device_roles',
                'preselected_tags',
                'save_coords',
                'show_unconnected',
                'show_cables',
                'show_logical_connections',
                'show_single_cable_logical_conns',
                'show_neighbors',
                'show_circuit',
                'show_power',
                'show_wireless',
                'draw_default_layout',
            ),
        ),
    )

    user_id = forms.CharField(widget=forms.HiddenInput())

    ignore_cable_type = forms.MultipleChoiceField(
        label=_('Ignore Termination Types'), 
        required=False, 
        choices=IndividualOptions.CHOICES,
        help_text=_('Choose Termination Types that you want to be ignored. '
            'If any ignored Termination Type is part of a connection, the '
            'cable is not displayed.')
    )
    preselected_device_roles = DynamicModelMultipleChoiceField(
        label=_('Preselected Device Role'),
        queryset=DeviceRole.objects.all(),
        required=False,
        help_text=_('Select Device Roles that you want to have '
            'preselected in the filter tab.')
    )
    preselected_tags = forms.ModelMultipleChoiceField(
        label=_('Preselected Tags'),
        queryset=Device.tags.all(),
        required=False,
        help_text=_('Select Tags that you want to have '
            'preselected in the filter tab.')
    )
    save_coords = forms.BooleanField(
        label=_('Save Coordinates'), 
        required=False, 
        initial=False,
        help_text=_('Coordinates of nodes will be saved if dragged to a different '
            'position. This option depends on parameters set in the config file. '
            'It has no effect if \'allow_coordinates_saving\' has not been set or '
            ' \'always_save_coordinates\' has been set.')
    )
    show_unconnected = forms.BooleanField(
        label=_('Show Unconnected'), 
        required=False, 
        initial=False,
        help_text=_('Draws devices that have no connections or for which no '
            'connection is displayed. This option depends on other parameters '
            'like \'Show Cables\' and \'Show Logical Connections\'.')
    )
    show_cables = forms.BooleanField(
        label =_('Show Cables'), 
        required=False, 
        initial=False,
        help_text=_('Displays connections between interfaces that are connected '
            'with one or more cables. These connections are displayed as solid '
            'lines in the color of the cable.')
    )
    show_logical_connections = forms.BooleanField(
        label =_('Show Logical Connections'), 
        required=False, 
        initial=False,
        help_text=_('Displays connections between devices that are not '
            'directly connected (e.g. via patch panels). These connections '
            'are displayed as yellow dotted lines.')
    )
    show_single_cable_logical_conns = forms.BooleanField(
        label = ('Show redundant Cable and Logical Connection'),
        required = False,
        initial=False,
        help_text=_('Shows a logical connection (in addition to a cable), '
            'even if a cable is directly connected. Leaving this option '
            'disabled prevents that redundant display. This option only '
            'has an effect if \'Show Logical Connections\' is activated.')
    )
    show_neighbors = forms.BooleanField(
        label =_('Show Neighbors'), 
        required=False, 
        initial=False,
        help_text=_('Adds neighbors to the filter result set automatically. '
            'Link peers will be added if \'Show Cables\' is ticked, far-end '
            'terminations will be added if \'Show Logical Connections\' is ticked.')
    )
    show_circuit = forms.BooleanField(
        label=_('Show Circuit Terminations'), 
        required=False, 
        initial=False,
        help_text=_('Displays connections between circuit terminations. '
            'These connections are displayed as blue dashed lines.')
    )
    show_power = forms.BooleanField(
        label=_('Show Power Feeds'), 
        required=False, 
        initial=False,
        help_text=_('Displays connections between power outlets and power '
            'ports. These connections are displayed as solid lines in the '
            'color of the cable. This option depends on \'Show Cables\'.')
    )
    show_wireless = forms.BooleanField(
        label =_('Show Wireless Links'), 
        required=False, 
        initial=False,
        help_text=_('Displays wireless connections. These connections are '
            'displayed as blue dotted lines.')
    )
    draw_default_layout = forms.BooleanField(
        label = ('Draw Default Layout'),
        required=False,
        initial=False,
        help_text=_('Enable this option if you want to draw the topology on '
            'the initial load (when you go to the topology plugin page).')
    )

    class Meta:
        model = IndividualOptions
        fields = [
            'user_id', 'ignore_cable_type', 'preselected_device_roles', 'preselected_tags', 'save_coords', 'show_unconnected', 'show_cables', 'show_logical_connections', 'show_single_cable_logical_conns', 'show_neighbors', 'show_circuit', 'show_power', 'show_wireless', 'draw_default_layout'
        ]        
