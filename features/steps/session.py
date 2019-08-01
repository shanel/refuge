from behave import *

@given(u'the session does not currenty exist in the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the session does not currenty exist in the system')


@when(u'we pass in the requisite session data')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we pass in the requisite session data')


@then(u'a barebones session is created.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then a barebones session is created.')


@given(u'the session exists in the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the session exists in the system')


@when(u'we request the session\'s data')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we request the session\'s data')


@then(u'we get the requested session\'s data.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then we get the requested session\'s data.')


@when(u'we pass in the fields to be updated for the session')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we pass in the fields to be updated for the session')


@then(u'the requested session\'s data is updated accordingly.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the requested session\'s data is updated accordingly.')


@when(u'we request the session be deleted from the system')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we request the session be deleted from the system')


@then(u'the session\'s data is deleted from the system.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the session\'s data is deleted from the system.')
