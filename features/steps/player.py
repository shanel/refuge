from behave import *

@given(u'the player does not currenty exist in the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the player does not currenty exist in the system')


@when(u'we pass in the requisite player data')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we pass in the requisite player data')


@then(u'a barebones player is created.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then a barebones player is created.')


@given(u'the player exists in the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the player exists in the system')


@when(u'we request the player\'s data')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we request the player\'s data')


@then(u'we get the requested player\'s data.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then we get the requested player\'s data.')


@when(u'we pass in the fields to be updated for the player')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we pass in the fields to be updated for the player')


@then(u'the requested player\'s data is updated accordingly.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the requested player\'s data is updated accordingly.')


@when(u'we request the player be deleted from the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we request the player be deleted from the system')


@then(u'the player\'s data is deleted from the system.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the player\'s data is deleted from the system.')
