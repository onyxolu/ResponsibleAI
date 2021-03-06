from azureml.core import Workspace
from azureml.exceptions import ComputeTargetException
from azureml.core.compute import ComputeTarget, DatabricksCompute, AmlCompute


def get_compute_aml(
    workspace: Workspace,
    compute_name: str,
    vm_size: str
):
    try:
        if compute_name in workspace.compute_targets:
            compute_target = workspace.compute_targets[compute_name]
            if compute_target and type(compute_target) is AmlCompute:
                print('Found existing compute target ' + compute_name
                      + ' so using it.')
        else:
            compute_config = AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                vm_priority="lowpriority",
                min_nodes=int(0),
                max_nodes=int(4),
                idle_seconds_before_scaledown="300"
            )
            compute_target = ComputeTarget.create(workspace, compute_name,
                                                  compute_config)
            compute_target.wait_for_completion(
                show_output=True,
                min_node_count=None,
                timeout_in_minutes=10)
        return compute_target
    except ComputeTargetException as e:
        print(e)
        print('An error occurred trying to provision compute.')
        exit()


def get_compute_databricks(
    workspace: Workspace,
    dbcomputename: str,
    resource_group: str,
    dbworkspace: str,
    dbaccesstoken: str
):
    try:
        databricks_compute = DatabricksCompute(
            workspace=workspace,
            name=dbcomputename)
        print('Compute target {} already exists'.format(dbcomputename))
    except ComputeTargetException:
        print('Compute not found, will use below parameters to attach new one')
        print('db_compute_name {}'.format(dbcomputename))
        print('db_resource_group {}'.format(resource_group))
        print('db_workspace_name {}'.format(dbworkspace))

        config = DatabricksCompute.attach_configuration(
            resource_group=resource_group,
            workspace_name=dbworkspace,
            access_token=dbaccesstoken)

        databricks_compute = ComputeTarget.attach(
            workspace,
            dbcomputename,
            config)
        databricks_compute.wait_for_completion(True)
    return databricks_compute
